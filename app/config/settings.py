from functools import lru_cache
from typing import List, Optional

from pydantic import AliasChoices, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Every environment variable the app reads, parsed and typed once.

    Flask config classes (app/config/{base,development,testing,production}.py)
    just copy fields off a single cached ``Settings()`` instance instead of
    calling ``os.environ.get`` themselves.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_env: str = Field(
        "development", validation_alias=AliasChoices("APP_ENV", "FLASK_ENV")
    )
    secret_key: str = Field("you-will-never-guess", alias="SECRET_KEY")

    # --- Database (PostgreSQL) ---------------------------------------------
    postgres_user: str = Field("marketplace", alias="POSTGRES_USER")
    postgres_password: str = Field("marketplace", alias="POSTGRES_PASSWORD")
    postgres_host: str = Field("localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")
    postgres_db: str = Field("marketplace", alias="POSTGRES_DB")
    database_url: Optional[str] = Field(None, alias="DATABASE_URL")
    test_database_url: Optional[str] = Field(None, alias="TEST_DATABASE_URL")

    # --- Redis ---------------------------------------------------------------
    redis_host: str = Field("localhost", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    redis_db: int = Field(0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(None, alias="REDIS_PASSWORD")
    redis_url: Optional[str] = Field(None, alias="REDIS_URL")
    test_redis_host: str = Field("localhost", alias="TEST_REDIS_HOST")
    test_redis_db: int = Field(1, alias="TEST_REDIS_DB")

    # --- JWT (flask-jwt-extended) --------------------------------------------
    jwt_secret_key: Optional[str] = Field(None, alias="JWT_SECRET_KEY")
    jwt_access_token_expires: int = Field(3600, alias="JWT_ACCESS_TOKEN_EXPIRES")
    jwt_refresh_token_expires: int = Field(2592000, alias="JWT_REFRESH_TOKEN_EXPIRES")

    # --- Mail ------------------------------------------------------------------
    mail_server: str = Field("smtp.googlemail.com", alias="MAIL_SERVER")
    mail_port: int = Field(587, alias="MAIL_PORT")
    mail_use_tls: bool = Field(True, alias="MAIL_USE_TLS")
    mail_username: Optional[str] = Field(None, alias="MAIL_USERNAME")
    mail_password: Optional[str] = Field(None, alias="MAIL_PASSWORD")
    admins: str = Field("", alias="ADMINS")

    app_host: str = Field("http://localhost:5000", alias="APP_HOST")

    # --- Logging / observability --------------------------------------------
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    gchat_webhook: Optional[str] = Field(None, alias="GCHAT_WEBHOOK")
    sentry_dsn: Optional[str] = Field(None, alias="SENTRY_DSN")

    @computed_field  # type: ignore[misc]
    @property
    def sqlalchemy_database_uri(self) -> str:
        return self.database_url or (
            "postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}".format(
                user=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                db=self.postgres_db,
            )
        )

    @computed_field  # type: ignore[misc]
    @property
    def redis_connection_url(self) -> str:
        if self.redis_url:
            return self.redis_url
        auth = ":{}@".format(self.redis_password) if self.redis_password else ""
        return "redis://{auth}{host}:{port}/{db}".format(
            auth=auth, host=self.redis_host, port=self.redis_port, db=self.redis_db
        )

    @computed_field  # type: ignore[misc]
    @property
    def admins_list(self) -> List[str]:
        return [admin for admin in self.admins.split(",") if admin]

    @computed_field  # type: ignore[misc]
    @property
    def effective_jwt_secret_key(self) -> str:
        return self.jwt_secret_key or self.secret_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
