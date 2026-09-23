from flask import Blueprint, Response, jsonify, url_for

from . import build_spec

_SWAGGER_UI_HTML = """<!doctype html>
<html>
  <head>
    <title>API Docs</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.onload = () => SwaggerUIBundle({{ url: "{spec_url}", dom_id: "#swagger-ui" }});
    </script>
  </body>
</html>"""


def register_docs(target, spec_path="/openapi.json", ui_path="/docs", endpoint_suffix="", **spec_kwargs):
    """Registers a spec JSON route + a Swagger UI route on `target` (a Flask
    app or Blueprint). `endpoint_suffix` avoids endpoint-name collisions
    when mounting more than one docs UI on the same target."""
    json_endpoint = f"_apidocs_openapi_json{endpoint_suffix}"
    ui_endpoint = f"_apidocs_swagger_ui{endpoint_suffix}"
    is_blueprint = isinstance(target, Blueprint)

    @target.route(spec_path, endpoint=json_endpoint)
    def _openapi_json():
        return jsonify(build_spec(**spec_kwargs))

    @target.route(ui_path, endpoint=ui_endpoint)
    def _swagger_ui():
        full_json_endpoint = f"{target.name}.{json_endpoint}" if is_blueprint else json_endpoint
        spec_url = url_for(full_json_endpoint)
        return Response(_SWAGGER_UI_HTML.format(spec_url=spec_url), mimetype="text/html")

    return target
