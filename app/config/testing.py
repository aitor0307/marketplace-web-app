import os

from .base import Config, basedir, settings


class TestingConfig(Config):
    ENV = "testing"
    DEBUG = True
    TESTING = True

    # Tests default to a local sqlite file unless a real Postgres test
    # database is provided, so the suite can run without infra.
    SQLALCHEMY_DATABASE_URI = settings.test_database_url or "sqlite:///" + os.path.join(
        basedir, "test.db"
    )

    WTF_CSRF_ENABLED = False

    # Never touch a real Redis instance from tests.
    REDIS_HOST = settings.test_redis_host
    REDIS_DB = settings.test_redis_db

    JWT_ACCESS_TOKEN_EXPIRES = 300
