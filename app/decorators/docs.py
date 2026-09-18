"""Minimal, dependency-free OpenAPI-style documentation for operation routes.

Every operation endpoint is decorated with ``@api_doc(...)``. The decorator
just records metadata on the function; ``build_openapi_spec`` later walks
the registered routes and turns that metadata into a real OpenAPI document,
served at ``/api/v1/docs`` (JSON) and ``/api/v1/docs/ui`` (Swagger UI).
"""
from flask import Blueprint, jsonify, render_template_string

_registry = {}

docs_bp = Blueprint("docs", __name__)

_SWAGGER_UI_HTML = """
<!doctype html>
<html>
  <head>
    <title>Marketplace API docs</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.onload = () => SwaggerUIBundle({ url: "/api/v1/docs", dom_id: "#swagger-ui" });
    </script>
  </body>
</html>
"""


def api_doc(summary, description="", tags=None, auth=True):
    """Attach OpenAPI metadata to an operation endpoint function."""

    def decorator(view_func):
        _registry[view_func] = {
            "summary": summary,
            "description": description,
            "tags": tags or [],
            "auth": auth,
        }
        return view_func

    return decorator


def build_openapi_spec(app):
    paths = {}
    for rule in app.url_map.iter_rules():
        view_func = app.view_functions.get(rule.endpoint)
        meta = _registry.get(view_func)
        if meta is None:
            continue

        path = rule.rule
        # Flask's <id> -> OpenAPI's {id}
        for arg in rule.arguments:
            path = path.replace("<{}>".format(arg), "{{{}}}".format(arg))

        methods = sorted((rule.methods or set()) - {"HEAD", "OPTIONS"})
        operation = {
            "summary": meta["summary"],
            "description": meta["description"],
            "tags": meta["tags"],
            "responses": {"200": {"description": "Success"}},
        }
        if meta["auth"]:
            operation["security"] = [{"bearerAuth": []}]
        operation["parameters"] = [
            {"name": arg, "in": "path", "required": True, "schema": {"type": "string"}}
            for arg in rule.arguments
        ]

        path_item = paths.setdefault(path, {})
        for method in methods:
            path_item[method.lower()] = operation

    return {
        "openapi": "3.0.3",
        "info": {"title": "Marketplace API", "version": "1"},
        "components": {
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
            }
        },
        "paths": paths,
    }


@docs_bp.route("/docs")
def openapi_json():
    from flask import current_app

    return jsonify(build_openapi_spec(current_app))


@docs_bp.route("/docs/ui")
def swagger_ui():
    return render_template_string(_SWAGGER_UI_HTML)
