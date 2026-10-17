from .base import Config, settings


class TestingConfig(Config):
    ENV = "testing"
    DEBUG = True
    TESTING = True

    # Tests need real Postgres (listing search uses pg_trgm/unaccent). The
    # default is the marketplace_test database of docker-compose.local.yml's
    # db service; CI points TEST_DATABASE_URL at its own service container.
    # The suite drops every table after each test: never aim it at real data.
    SQLALCHEMY_DATABASE_URI = (
        settings.test_database_url
        or "postgresql+psycopg2://marketplace:marketplace@localhost:5432/marketplace_test"
    )

    WTF_CSRF_ENABLED = False

    # Never touch a real Redis instance from tests.
    REDIS_HOST = settings.test_redis_host
    REDIS_DB = settings.test_redis_db

    JWT_ACCESS_TOKEN_EXPIRES = 300

    # Deliver inline so tests can inspect sent mail (Flask-Mail suppresses
    # actual sending under TESTING).
    MAIL_SEND_ASYNC = False
    MAIL_USERNAME = "sender@example.com"
    NOREPLY_MAIL_USERNAME = "noreply@example.com"
    NOREPLY_MAIL_PASSWORD = "noreply-password"

    REGISTRATION_KEY = "test-registration-key"
    REGISTRATION_APPROVER_EMAIL = "approver@example.com"
    REGISTRATION_CONTACT_EMAIL = "support@example.com"
    FEEDBACK_EMAIL = "feedback@example.com"
