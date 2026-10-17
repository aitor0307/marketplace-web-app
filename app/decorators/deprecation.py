"""Marks whole blueprints as deprecated without changing what they serve.

The Jinja views are superseded by the React app in frontend/ but stay
mounted until it fully replaces them. Every response they produce carries
the standard ``Deprecation`` header (plus a ``Link`` to the successor when
FRONTEND_URL is configured), and the first hit on each endpoint is logged
so we can see what still gets traffic before deleting it.
"""
from flask import current_app, request

from app.utils.logger import logger


def deprecate_blueprint(blueprint, successors=None):
    """Factory: registers the deprecation hooks on ``blueprint`` and returns it.

    :param successors: optional ``{endpoint: path_template}`` mapping each view
        to the SPA route replacing it, formatted with the view args
        (e.g. ``{"views_listings.listing_detail": "/listings/{listing_id}"}``).
        Unmapped endpoints point at the SPA root.
    """
    successors = successors or {}
    reported_endpoints = set()

    @blueprint.after_request
    def _mark_deprecated(response):
        response.headers["Deprecation"] = "true"

        frontend_url = current_app.config.get("FRONTEND_URL")
        if frontend_url:
            path = successors.get(request.endpoint, "/").format(**(request.view_args or {}))
            response.headers["Link"] = '<{}{}>; rel="successor-version"'.format(
                frontend_url.rstrip("/"), path
            )

        if request.endpoint not in reported_endpoints:
            reported_endpoints.add(request.endpoint)
            logger.warning(f"[DEPRECATED] Jinja view '{request.endpoint}' served; use the React frontend")
        return response

    return blueprint
