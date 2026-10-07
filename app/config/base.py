import logging
import os

from app.config.settings import get_settings

basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
settings = get_settings()


class Config:
    """Base configuration shared by every environment.

    Every value here is copied straight off the cached ``Settings()``
    instance (see app/config/settings.py) instead of reading the
    environment itself; environment-specific classes only override what
    actually differs.
    """

    ENV = "base"
    DEBUG = False
    TESTING = False

    # app.utils.logger reads this directly (it's imported before any app
    # exists), so it mirrors settings.app_env rather than the per-subclass
    # ENV label above.
    ENVIRONMENT = settings.app_env

    SECRET_KEY = settings.secret_key

    # --- Database (PostgreSQL) -----------------------------------------------
    SQLALCHEMY_DATABASE_URI = settings.sqlalchemy_database_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # --- Redis -----------------------------------------------------------------
    # Not used by any feature yet, but wired up end to end (client, health
    # check, config) so it is a config flag away when we add caching,
    # rate limiting, or vector search (e.g. RediSearch/redis-vector).
    REDIS_HOST = settings.redis_host
    REDIS_PORT = settings.redis_port
    REDIS_DB = settings.redis_db
    REDIS_PASSWORD = settings.redis_password
    REDIS_URL = settings.redis_connection_url

    # --- JWT (flask-jwt-extended) ----------------------------------------------
    JWT_SECRET_KEY = settings.effective_jwt_secret_key
    JWT_ACCESS_TOKEN_EXPIRES = settings.jwt_access_token_expires
    JWT_REFRESH_TOKEN_EXPIRES = settings.jwt_refresh_token_expires
    JWT_TOKEN_LOCATION = ["headers"]

    # --- Uploads -----------------------------------------------------------------
    IMAGES_FOLDER = os.path.join(basedir, "app", "static", "listing_images")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB, for the whole request (all images together)
    MAX_LISTING_IMAGES = 10

    # --- Mail (Gmail SMTP) --------------------------------------------------------
    # Everything but the app password is a constant; override per environment
    # in the subclasses if one needs a different account.
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    # Gmail account the app sends from; also used as the From address.
    MAIL_USERNAME = "aitor.gastaminza@clubesquivaldaran.com"
    MAIL_PASSWORD = settings.mail_password
    ADMINS = settings.admins_list

    HOST = settings.app_host

    # --- React frontend --------------------------------------------------------
    FRONTEND_URL = settings.frontend_url
    CORS_ORIGINS = settings.cors_origins_list

    # --- Logging / observability --------------------------------------------
    LOG_LEVEL = getattr(logging, settings.log_level.upper(), logging.INFO)
    GCHAT_WEBHOOK = settings.gchat_webhook
    SENTRY_DSN = settings.sentry_dsn

    # --- OAuth login -----------------------------------------------------------
    GOOGLE_OAUTH_CLIENT_ID = settings.google_oauth_client_id

    # --- Registration approval ---------------------------------------------------
    REGISTRATION_KEY = settings.registration_key
    REGISTRATION_APPROVER_EMAIL = settings.registration_approver_email
    REGISTRATION_APPROVAL_MAX_AGE = 30 * 24 * 3600  # how long an approval link stays valid (seconds)

    @staticmethod
    def init_app(app):
        """Hook for environment-specific runtime setup (logging, etc.)."""
        pass
