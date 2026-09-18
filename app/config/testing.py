import os

from .base import Config, basedir


class TestingConfig(Config):
    ENV = "testing"
    DEBUG = True
    TESTING = True

    # Tests default to a local sqlite file unless a real Postgres test
    # database is provided, so the suite can run without infra.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "sqlite:///" + os.path.join(basedir, "test.db")
    )

    WTF_CSRF_ENABLED = False

    # Never touch a real Redis instance from tests.
    REDIS_HOST = os.environ.get("TEST_REDIS_HOST", "localhost")
    REDIS_DB = int(os.environ.get("TEST_REDIS_DB", 1))

    JWT_ACCESS_TOKEN_EXPIRES = 300
