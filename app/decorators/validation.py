from functools import wraps

from flask import request
from pydantic import ValidationError

from app.models.api_base import ResponseFactory


def validate_payload(schema, source="json"):
    """Parse and validate the incoming request data against a pydantic model.

    ``source`` picks where the raw data comes from:
      - "json": ``request.get_json()`` (the default, for JSON bodies)
      - "form": ``request.form`` (multipart endpoints that also take a file)
      - "query": ``request.args`` (GET filters/pagination)

    The validated model is injected into the view as the ``payload``
    keyword argument; this is the only place any operation reads raw
    request data.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if source == "json":
                raw = request.get_json(silent=True) or {}
            elif source == "form":
                raw = request.form.to_dict()
            else:
                raw = request.args.to_dict()

            try:
                payload = schema.model_validate(raw)
            except ValidationError as exc:
                return ResponseFactory.bad_request(exc.errors())

            kwargs["payload"] = payload
            return fn(*args, **kwargs)

        return wrapper

    return decorator
