import os

from .base import Config
from .development import DevelopmentConfig
from .testing import TestingConfig
from .production import ProductionConfig

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name=None):
    """Resolve a config class by name, falling back to APP_ENV/FLASK_ENV."""
    config_name = config_name or os.environ.get("APP_ENV") or os.environ.get(
        "FLASK_ENV", "default"
    )
    return config_by_name.get(config_name, config_by_name["default"])
