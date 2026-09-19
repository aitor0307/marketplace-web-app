"""Framework-agnostic OpenAPI spec builder on top of apispec.

Routes are documented with @document(...) (or app.decorators.docs.api_doc,
the Flask + pydantic convenience wrapper around this that the app's route
files actually use) without repeating their own path/method: the real
values are resolved later, by walking the live Flask app's url_map when
the spec is actually built (build_spec(), normally called from inside the
Flask view that serves the JSON spec). That is what keeps the generated
spec from ever drifting out of sync with the routes actually registered -
there's nothing to hand-keep-in-sync, because path/method aren't typed
twice in the first place.
"""
import copy
import re

from apispec import APISpec

_REGISTRY = []   # every documented endpoint, once resolved
_PENDING = []    # @document(...) calls awaiting path/method resolution
_LIVE_APPS = []  # apps explicitly registered for live resolution


def register_app(app):
    """Explicitly register a live Flask app for live-mode resolution.

    Not needed when build_spec() runs inside a Flask request (the current
    app is picked up automatically); useful for building the spec outside
    of a request, e.g. from a script.
    """
    _LIVE_APPS.append(app)


def document(path=None, method=None, **kwargs):
    """Decorator that documents an endpoint.

    - Explicit: document("/items/{item_id}", "get", ...) registers
      immediately, with path/method exactly as given.
    - Live (path omitted, the normal case): stashes the function plus its
      metadata; the real path/method/path-parameters are resolved from
      the live app's url_map when build_spec() runs, matched by comparing
      function objects.
    """

    def wrapper(func):
        if path is None:
            _PENDING.append({"func": func, "method": method, "kwargs": kwargs})
        else:
            _register(path, method, **kwargs)
        return func

    return wrapper


def _register(path, method, tags=None, summary="", description="", hidden=False, **openapi_fields):
    _REGISTRY.append({
        "path": path,
        "method": method.lower(),
        "operation": {
            "summary": summary,
            "description": description,
            "tags": tags or [],
            **openapi_fields,
        },
        "hidden": hidden,
    })


def _werkzeug_rule_to_openapi_path(rule):
    """Converts '<int:listing_id>' or '<listing_id>' to '{listing_id}'."""
    return re.sub(r"<(?:[^:<>]+:)?([^<>]+)>", r"{\1}", rule)


def _iter_routes(app):
    """Yields (func, path, methods, path_args) for every registered route."""
    for rule in app.url_map.iter_rules():
        func = app.view_functions.get(rule.endpoint)
        if func is None:
            continue
        path = _werkzeug_rule_to_openapi_path(rule.rule)
        methods = {m.lower() for m in (rule.methods or set()) - {"HEAD", "OPTIONS"}}
        yield func, path, methods, set(rule.arguments)


def _live_apps():
    apps = list(_LIVE_APPS)
    try:
        from flask import current_app
        apps.append(current_app._get_current_object())
    except Exception:
        pass
    return apps


def _resolve_pending():
    """Flushes live-mode entries into the registry, resolving path/method
    and auto-adding path parameters against the live app(s)."""
    pending_entries = list(_PENDING)
    _PENDING.clear()
    apps = _live_apps()

    for pending in pending_entries:
        func = pending["func"]
        match = next(
            (
                (path, methods, path_args)
                for app in apps
                for f, path, methods, path_args in _iter_routes(app)
                if f is func
            ),
            None,
        )
        if match is None:
            continue

        path, real_methods, path_args = match
        methods = [pending["method"].lower()] if pending["method"] else list(real_methods)

        kwargs = dict(pending["kwargs"])
        if path_args:
            declared_params = list(kwargs.get("parameters", []))
            declared_names = {p["name"] for p in declared_params}
            auto_params = [path_param(arg) for arg in sorted(path_args) if arg not in declared_names]
            kwargs["parameters"] = auto_params + declared_params

        for method in methods:
            _register(path, method, **kwargs)


def get_registry():
    return copy.deepcopy(_REGISTRY)


def clear_registry():
    _REGISTRY.clear()


def _is_hidden(entry, hidden_tags):
    if entry["hidden"]:
        return True
    return bool(set(entry["operation"].get("tags", [])) & set(hidden_tags))


def build_spec(title="API Documentation", version="1.0.0", hidden_tags=None):
    """Builds the final OpenAPI spec from the registry."""
    if _PENDING:
        _resolve_pending()

    spec = APISpec(title=title, version=version, openapi_version="3.0.3")
    spec.components.security_scheme(
        "bearerAuth", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )

    for entry in get_registry():
        if _is_hidden(entry, hidden_tags or []):
            continue
        spec.path(path=entry["path"], operations={entry["method"]: entry["operation"]})

    return spec.to_dict()


# --- Pydantic-model-driven schema helpers -----------------------------------

def _inline_defs(schema):
    """Inlines pydantic's $defs refs so the schema is self-contained
    wherever it ends up embedded (Swagger UI can't resolve #/$defs/Name
    once it's nested a few levels under paths/*/requestBody)."""
    defs = schema.get("$defs")
    if not defs:
        return schema

    def resolve(node, seen=()):
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/$defs/"):
                name = ref.split("/")[-1]
                if name in seen:
                    return {}
                return resolve(copy.deepcopy(defs.get(name, {})), seen + (name,))
            return {k: resolve(v, seen) for k, v in node.items() if k not in ("$defs", "discriminator")}
        if isinstance(node, list):
            return [resolve(item, seen) for item in node]
        return node

    return resolve(schema)


def _model_schema(model):
    return _inline_defs(model.model_json_schema())


def pydantic_body(model, content_type="application/json"):
    """Builds a requestBody straight from a pydantic model's JSON Schema -
    the same model that actually validates the request (Model(**data))."""
    return {"required": True, "content": {content_type: {"schema": _model_schema(model)}}}


def json_body(fields, required=None):
    return {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": fields,
                    "required": required if required is not None else list(fields.keys()),
                }
            }
        },
    }


def json_response(schema, description=""):
    return {"description": description, "content": {"application/json": {"schema": schema}}}


def pydantic_response(model, description=""):
    return json_response(_model_schema(model), description)


def pydantic_list_response(model, description=""):
    return json_response({"type": "array", "items": _model_schema(model)}, description)


_STATUS_CODES = {
    "ok": "200", "created": "201", "no_content": "204", "bad_request": "400",
    "unauthorized": "401", "forbidden": "403", "not_found": "404",
    "conflict": "409", "server_error": "500",
}


def responses(**kwargs):
    """Friendly-name shorthand for a `responses=` dict, e.g.
    responses(created=pydantic_response(AuthResponse), conflict=json_response(...))."""
    return {_STATUS_CODES.get(name, name): value for name, value in kwargs.items()}


def path_param(name, schema_type="integer"):
    return {"name": name, "in": "path", "required": True, "schema": {"type": schema_type}}


def query_param(name, schema_type="string", required=False):
    return {"name": name, "in": "query", "required": required, "schema": {"type": schema_type}}


def pydantic_query_params(model):
    """Derives `parameters` (in: query) from a pydantic model's fields, for
    GET endpoints whose filters are validated as
    Model(**request.args.to_dict()) rather than a JSON body."""
    schema = model.model_json_schema()
    required = set(schema.get("required", []))
    params = []
    for field_name, field_schema in schema.get("properties", {}).items():
        field_type = field_schema.get("type")
        if field_type is None and "anyOf" in field_schema:
            field_type = next(
                (s["type"] for s in field_schema["anyOf"] if s.get("type") != "null"), "string"
            )
        params.append(query_param(field_name, field_type or "string", field_name in required))
    return params
