from flask import render_template
from pydantic import ValidationError

from app.extensions import db
from app.models.api_base import ResponseFactory


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("error.html", title="Page Not Found", error=error), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("error.html", title="Error, whoops!", error=error), 500

    @app.errorhandler(ValidationError)
    def invalid_payload(error):
        # Operations build their pydantic model straight from the request
        # data (Schema(**request.get_json())); this is what turns the
        # ValidationError that construction raises into an HTTP response.
        return ResponseFactory.bad_request(error.errors())
