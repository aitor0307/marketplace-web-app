# app/__init__alembic.py
"""Minimal app factory for `flask db migrate/upgrade/downgrade`.

Loading the full create_app() (app/__init__.py) to run migrations would also
wire up Flask-Login, Flask-Mail, JWT, Redis and every blueprint -- none of
which Alembic touches, and any of which can fail to initialize in a dev
environment that doesn't have SMTP/Redis/OAuth credentials set. This factory
only sets up what migrations/env.py actually needs: config, db and migrate.
"""
from flask import Flask

from app.config import get_config
from app.extensions import db, migrate


def create_app(config_name=None):
    app = Flask(__name__)

    config_class = get_config(config_name)
    app.config.from_object(config_class)
    config_class.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models  # noqa: F401  (registers every model on db.metadata)

    return app
