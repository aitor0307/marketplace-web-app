import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class Config:
    """Base configuration shared by every environment.

    Environment-specific classes only override what actually differs;
    anything read from the environment here already has a safe default.
    """

    ENV = "base"
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.environ.get("SECRET_KEY", "you-will-never-guess")

    # --- Database (PostgreSQL) -------------------------------------------------
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "marketplace")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "marketplace")
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "marketplace")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}".format(
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            db=POSTGRES_DB,
        ),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # --- Redis -------------------------------------------------------------
    # Not used by any feature yet, but wired up end to end (client, health
    # check, config) so it is a config flag away when we add caching,
    # rate limiting, or vector search (e.g. RediSearch/redis-vector).
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
    REDIS_DB = int(os.environ.get("REDIS_DB", 0))
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
    REDIS_URL = os.environ.get(
        "REDIS_URL",
        "redis://{auth}{host}:{port}/{db}".format(
            auth=(":" + REDIS_PASSWORD + "@") if REDIS_PASSWORD else "",
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
        ),
    )

    # --- JWT (flask-jwt-extended) -------------------------------------------
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES", 2592000))
    JWT_TOKEN_LOCATION = ["headers"]

    # --- Uploads -------------------------------------------------------------
    IMAGES_FOLDER = os.path.join(basedir, "app", "static", "listing_images")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # --- Mail ----------------------------------------------------------------
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.googlemail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = bool(int(os.environ.get("MAIL_USE_TLS", 1)))
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = [a for a in os.environ.get("ADMINS", "").split(",") if a]

    HOST = os.environ.get("APP_HOST", "http://localhost:5000")

    @staticmethod
    def init_app(app):
        """Hook for environment-specific runtime setup (logging, etc.)."""
        pass
