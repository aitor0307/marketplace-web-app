import contextvars
import functools
import json
import logging
import os
import re
import sys
import traceback

import requests
import sentry_sdk
from flask import g, has_request_context, request
from opentelemetry import trace
from sentry_sdk import capture_exception

from app.config import get_config

Config = get_config()

if Config.SENTRY_DSN:
    sentry_sdk.init(dsn=Config.SENTRY_DSN, environment=Config.ENVIRONMENT)

HEALTH = 15
logging.addLevelName(HEALTH, "HEALTH")

# Carries log context across both Flask requests and Celery/background
# threads, which don't have a Flask ``g`` to write to.
_logging_context: "contextvars.ContextVar[dict]" = contextvars.ContextVar(
    "logging_context", default={}
)

# No telemetry backend is wired up in this app yet; this is an inert
# placeholder so Logger.__init__ has a handler to attach without a real
# OTel exporter configured. Swap in a real OTel LoggingHandler (e.g.
# opentelemetry.sdk._logs.LoggingHandler) once telemetry infra is added.
otel_handler = logging.NullHandler()


class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.environment = Config.ENVIRONMENT
        context = _logging_context.get()

        if has_request_context():
            customdata = {
                "company_id": g.company_id if hasattr(g, "company_id") else "no_auth",
            }
            optional_fields = ["booking_id", "user_id", "apartment_id", "message_id"]
            for field in optional_fields:
                if hasattr(g, field):
                    customdata[field] = getattr(g, field)
            customdata.update(context)

            record.customdata = json.dumps(customdata)
            record.company_id = g.company_id if hasattr(g, "company_id") else context.get("company_id", "no_auth")
            record.sub = g.sub if hasattr(g, "sub") else context.get("sub", "no_user")
            record.service = "api"
            record.request_id = g.request_id if hasattr(g, "request_id") else context.get("request_id", "no_request_id")
            record.booking_id = context.get("booking_id") or (g.booking_id if hasattr(g, "booking_id") else None) or ""
        else:
            customdata = dict(context)
            record.customdata = json.dumps(customdata) if customdata else None
            record.request_id = context.get("request_id", "no_request_id")
            record.company_id = context.get("company_id", "no_auth")
            record.service = context.get("service", "non-api")
            record.booking_id = context.get("booking_id", "")

            if record.filename == "server.py" or record.name == 'app.websockets.routes':
                record.service = "websockets"
            elif record.name.startswith("gunicorn"):
                record.service = "gunicorn"
        return True


class CustomFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.api_path = request.path
            self.name = record.api_path.replace("/", ".")
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(name)s:%(funcName)s.L%(lineno)d - %(message)s'
        self._style._fmt = log_format
        record.filename = os.path.splitext(record.filename)[0]
        return super().format(record)


class LogRecordWrapper:
    """Wrapper for log records that adds a ``.notify()`` method.

    No ``.save()``: this app has no log tables / Celery log-persist task,
    so that half of the original wrapper is intentionally left out.
    """
    _channels_cache = None

    def __init__(self, msg, level, name):
        self.msg = msg
        self.level = level
        self.module = name

    @classmethod
    def _get_channels(cls):
        if cls._channels_cache is None:
            try:
                from app.models.general_settings import GeneralSettings
                raw = GeneralSettings.get("notification_channels")
                cls._channels_cache = json.loads(raw) if raw else {"robodreams": Config.GCHAT_WEBHOOK}
            except Exception:
                return {"robodreams": Config.GCHAT_WEBHOOK}
        return cls._channels_cache

    def notify(self, channel="robodreams"):
        """Notify the user with a message."""
        try:
            webhook_url = self._get_channels().get(channel)
            if not webhook_url:
                return
            message = {
                "text": f"[{self.level.upper()}]: *{Config.ENVIRONMENT}*\n```{self.msg}```"
            }
            requests.post(webhook_url, json=message)
        except Exception:
            pass


class Logger(logging.Logger):
    """Custom logger with OpenTelemetry integration and request context."""

    def __init__(self, name, level=Config.LOG_LEVEL, tracer=None):
        super().__init__(name, level)
        self.tracer = tracer or trace.get_tracer(name)
        self._current_span = None
        self.propagate = False  # Prevent duplicate logs from propagating to parent loggers

        if not self.handlers:
            handler = logging.StreamHandler(stream=sys.stdout)
            formatter = CustomFormatter()
            handler.setFormatter(formatter)
            self.addHandler(handler)

            self.addHandler(otel_handler)

            self.environment = Config.ENVIRONMENT
            self._configure_third_party_loggers()
            self.addFilter(RequestContextFilter())

    def _configure_third_party_loggers(self):
        third_party_loggers = {
            "Microsoft.AspNetCore.Hosting.Diagnostics": logging.WARNING,
            "microsoft.aspnetcore.hosting.diagnostics": logging.WARNING,
            "azure.core.pipeline.policies.http_logging_policy": logging.WARNING,
            "azure.monitor.opentelemetry.exporter.export._base": logging.WARNING,
            "sqlalchemy.engine": logging.WARNING,
            "deepl": logging.WARNING,
            "opentelemetry.attributes": logging.ERROR,
        }
        socket_level = logging.DEBUG if self.environment != "production" else logging.ERROR
        third_party_loggers.update({"socketio": socket_level, "engineio": socket_level})
        for logger_name, level in third_party_loggers.items():
            logging.getLogger(logger_name).setLevel(level)

    def set_context(self, **kwargs):
        """Works for both Flask requests (writes to g) and Celery/background
        threads (writes to a ContextVar), so call sites don't need to know which."""
        current_context = _logging_context.get().copy()
        current_context.update(kwargs)
        _logging_context.set(current_context)
        if has_request_context():
            for key, value in kwargs.items():
                setattr(g, key, value)

    def clear_context(self):
        _logging_context.set({})

    @staticmethod
    def _inject_event_from_msg(msg, kwargs):
        if "event" not in kwargs.get("extra", {}):
            match = re.match(r'^\[([^\]]+)\]', str(msg))
            if match:
                kwargs.setdefault("extra", {})["event"] = match.group(1).lower()

    # Custom logging methods with LogRecordWrapper return
    def error(self, msg, *args, **kwargs):
        kwargs.setdefault("stacklevel", 2)
        self._inject_event_from_msg(msg, kwargs)
        super().error(msg, *args, **kwargs)
        return LogRecordWrapper(msg, "ERROR", self.name)

    def debug(self, msg, *args, **kwargs):
        kwargs.setdefault("stacklevel", 2)
        self._inject_event_from_msg(msg, kwargs)
        super().debug(msg, *args, **kwargs)
        return LogRecordWrapper(msg, "DEBUG", self.name)

    def health(self, msg, *args, **kwargs):
        kwargs.setdefault("stacklevel", 2)
        self._inject_event_from_msg(msg, kwargs)
        if self.isEnabledFor(HEALTH):
            self._log(HEALTH, msg, args, **kwargs)
        return LogRecordWrapper(msg, "HEALTH", self.name)

    def info(self, msg, *args, **kwargs):
        kwargs.setdefault("stacklevel", 2)
        self._inject_event_from_msg(msg, kwargs)
        super().info(msg, *args, **kwargs)
        return LogRecordWrapper(msg, "INFO", self.name)

    def warning(self, msg, *args, **kwargs):
        kwargs.setdefault("stacklevel", 2)
        self._inject_event_from_msg(msg, kwargs)
        super().warning(msg, *args, **kwargs)
        return LogRecordWrapper(msg, "WARNING", self.name)

    def critical(self, msg, *args, **kwargs):
        kwargs.setdefault("stacklevel", 2)
        self._inject_event_from_msg(msg, kwargs)
        super().critical(msg, *args, **kwargs)
        return LogRecordWrapper(msg, "CRITICAL", self.name)

    def catch_exception(self, e, level="error", *args, **kwargs):
        """Log exception with full traceback and send to Sentry."""
        kwargs.setdefault("stacklevel", 2)
        exc_type, _exc_value, exc_tb = sys.exc_info()
        tb = traceback.extract_tb(exc_tb)
        last_trace = tb[-1]
        msg = f"[EXCEPTION]: {e} - {exc_type} - Line: {last_trace.lineno} in {last_trace.line}"

        log_method = getattr(super(), level, None)
        if callable(log_method):
            log_method(msg, *args, **kwargs)
        else:
            msg = f"[INVALID LEVEL '{level}'] {msg}"
            super().error(msg, *args, **kwargs)

        capture_exception(e)  # Send to Sentry
        return LogRecordWrapper(msg, level.upper(), self.name).notify()

    # Tracing methods
    def start_span(self, span_name, attributes=None):
        span = self.tracer.start_span(span_name)
        if attributes:
            span.set_attributes(attributes)
        return span

    def trace_operation(self, operation_name, attributes=None):
        return self.tracer.start_as_current_span(operation_name, attributes=attributes)

    def add_event(self, event_name, attributes=None):
        span = self._current_span or trace.get_current_span()
        if span and span.is_recording():
            span.add_event(event_name, attributes or {})
        body = json.dumps({"event": event_name, **(attributes or {})})
        self.info(body, extra={"event": event_name})

    def set_status(self, status_code, description=None):
        span = self._current_span or trace.get_current_span()
        if span and span.is_recording():
            from opentelemetry.trace import StatusCode
            span.set_status(StatusCode(status_code), description)

    def record_exception(self, exception):
        span = self._current_span or trace.get_current_span()
        if span and span.is_recording():
            span.record_exception(exception)

    def set_attribute(self, key, value):
        span = self._current_span or trace.get_current_span()
        if span and span.is_recording() and value is not None:
            span.set_attribute(key, value)

    def set_attributes(self, attributes):
        span = self._current_span or trace.get_current_span()
        if span and span.is_recording():
            span.set_attributes({k: v for k, v in attributes.items() if v is not None})

    @staticmethod
    def trace_route(span_name=None, route_name=None, attributes=None):
        """Decorator to automatically trace Flask routes with OpenTelemetry."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                tracer = trace.get_tracer(__name__)
                name = span_name or f"{func.__module__}.{func.__name__}"
                span_attributes = attributes or {}
                if route_name:
                    span_attributes["route.name"] = route_name
                if has_request_context():
                    span_attributes.update({
                        "http.method": request.method,
                        "http.url": request.url,
                        "http.route": request.endpoint,
                    })
                    if hasattr(g, "company_id") and g.company_id is not None:
                        span_attributes["company.id"] = g.company_id
                    if hasattr(g, "request_id") and g.request_id is not None:
                        span_attributes["request.id"] = g.request_id
                    if hasattr(g, "sub") and g.sub is not None:
                        span_attributes["sub"] = g.sub

                with tracer.start_as_current_span(name, attributes=span_attributes) as span:
                    logger_instance = None
                    try:
                        module = func.__module__
                        if hasattr(func, '__self__'):
                            if hasattr(func.__self__, 'logger') and isinstance(func.__self__.logger, Logger):
                                logger_instance = func.__self__.logger
                        else:
                            if module in sys.modules:
                                mod = sys.modules[module]
                                if hasattr(mod, 'logger') and isinstance(mod.logger, Logger):
                                    logger_instance = mod.logger

                        if logger_instance:
                            logger_instance._current_span = span

                        result = func(*args, **kwargs)

                        from opentelemetry.trace import StatusCode
                        span.set_status(StatusCode.OK)
                        return result

                    except Exception as e:
                        from opentelemetry.trace import StatusCode
                        span.set_status(StatusCode.ERROR, str(e))
                        span.record_exception(e)
                        raise
                    finally:
                        if logger_instance:
                            logger_instance._current_span = None

            return wrapper
        return decorator


# Deliberately NOT calling logging.setLoggerClass(Logger): third-party
# loggers configured in _configure_third_party_loggers (notably
# "sqlalchemy.engine", which is fetched via a plain logging.getLogger()
# call from inside that very method) would otherwise also be built as
# Logger instances, and building one recurses right back into
# _configure_third_party_loggers before it's registered in Python's
# logger cache - infinite recursion. Constructing our own logger directly
# sidesteps that: every other name in the process keeps the stdlib
# logging.Logger class, and only gets its level adjusted.
logger = Logger("marketplace")
