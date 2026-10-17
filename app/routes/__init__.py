from app.decorators.docs import docs_bp
from app.routes.operations import operations_blueprints
from app.routes.views import view_blueprints


def register_blueprints(app):
    for blueprint in view_blueprints:
        app.register_blueprint(blueprint)
    for blueprint in operations_blueprints:
        app.register_blueprint(blueprint)
    app.register_blueprint(docs_bp, url_prefix="/api/v1")
