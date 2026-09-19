"""Flask + pydantic convenience wrapper around tools.apidocs.

Kept as a thin adapter so route files can keep writing
@api_doc(summary, tags=..., auth=...) for the common case; anything that
needs more of apispec's power directly (custom parameters, response
schemas) imports the tools.apidocs helpers itself, as
app/routes/operations/auth_ops.py and listings_ops.py do.
"""
from flask import Blueprint

from tools.apidocs import document, pydantic_body
from tools.apidocs.ui import register_docs

docs_bp = Blueprint("docs", __name__)


def api_doc(
    summary,
    description="",
    tags=None,
    auth=True,
    request_model=None,
    request_content_type="application/json",
    **openapi_fields,
):
    """Documents an operation endpoint.

    Path/method aren't given here - they're resolved live against the
    real Flask route when the spec is built (see tools.apidocs), so they
    can never drift out of sync with what's actually registered.
    """
    fields = dict(openapi_fields)
    if auth:
        fields.setdefault("security", [{"bearerAuth": []}])
    if request_model is not None:
        fields.setdefault("requestBody", pydantic_body(request_model, request_content_type))
    fields.setdefault("responses", {"200": {"description": "Success"}})
    return document(summary=summary, description=description, tags=tags, **fields)


register_docs(docs_bp, spec_path="/docs", ui_path="/docs/ui", title="Marketplace API", version="1")
