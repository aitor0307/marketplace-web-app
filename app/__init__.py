from datetime import datetime

from flask import Flask
from flask_login import current_user

from app.config import get_config
from app.extensions import bootstrap, db, jwt, login, mail, migrate, moment, redis_client


def create_app(config_name=None):
    """Application factory: grabs the right config class and wires everything up."""
    app = Flask(__name__, static_url_path="/static")

    config_class = get_config(config_name)
    app.config.from_object(config_class)
    config_class.init_app(app)

    _init_extensions(app)
    _register_blueprints(app)
    _register_hooks(app)

    from app import errors

    errors.register_error_handlers(app)

    return app


def _init_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    jwt.init_app(app)
    redis_client.init_app(app)


def _register_blueprints(app):
    from app.routes import register_blueprints

    register_blueprints(app)


def _register_hooks(app):
    @app.before_request
    def update_last_seen():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
