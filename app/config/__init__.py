from .base import Config
from .development import DevelopmentConfig
from .production import ProductionConfig
from .settings import get_settings
from .testing import TestingConfig

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(config_name=None):
    """Resolve a config class by name, falling back to Settings.app_env."""
    config_name = config_name or get_settings().app_env
    return config_by_name.get(config_name, config_by_name["default"])
