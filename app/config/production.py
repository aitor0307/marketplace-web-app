import logging
from logging.handlers import RotatingFileHandler

from .base import Config


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        for required in ("SECRET_KEY", "SQLALCHEMY_DATABASE_URI", "JWT_SECRET_KEY"):
            if not app.config.get(required):
                raise RuntimeError(
                    "Missing required production setting: {}".format(required)
                )

        handler = RotatingFileHandler(
            "logs/marketplace.log", maxBytes=10 * 1024 * 1024, backupCount=10
        )
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
