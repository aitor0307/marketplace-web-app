from functools import lru_cache
from typing import List, Optional
from urllib.parse import quote_plus

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
        "development", validation_alias=AliasChoices("APP_ENV", "FLASK_ENV", "ENVIRONMENT")
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
    # Supabase Postgres connection string; production falls back to it when
    # DATABASE_URL is unset (see app/config/production.py).
    supabase_database_url: Optional[str] = Field(default=None, alias="SUPABASE_DATABASE_URL")
    # Pieces of the Supabase session pooler URL, used by supabase_connection_url
    # when SUPABASE_DATABASE_URL is unset (see app/config/local_supabase.py).
    supabase_project: Optional[str] = Field(default=None, alias="SUPABASE_PROJECT")
    supabase_region: Optional[str] = Field(default=None, alias="SUPABASE_REGION")
    supabase_password: Optional[str] = Field(default=None, alias="SUPABASE_PASSWORD")
    supabase_pooler: str = Field(default="aws-0", alias="SUPABASE_POOLER")
    supabase_port: int = Field(default=5432, alias="SUPABASE_PORT")
    supabase_db: str = Field(default="postgres", alias="SUPABASE_DB")

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
    # Server/port/TLS are constants in app/config/base.py.
    # Gmail account the app sends from (and its From address). Required for any mail.
    mail_username: Optional[str] = Field(default=None, alias="MAIL_USERNAME")
    mail_password: Optional[str] = Field(None, alias="MAIL_PASSWORD")
    # The account every user-facing email is sent from (see app/email.py).
    # Unset = send those from MAIL_USERNAME too.
    noreply_mail_username: Optional[str] = Field(default=None, alias="NOREPLY_MAIL_USERNAME")
    noreply_mail_password: Optional[str] = Field(default=None, alias="NOREPLY_MAIL_PASSWORD")
    admins: str = Field("", alias="ADMINS")

    app_host: str = Field("http://localhost:5000", alias="APP_HOST")

    # --- React frontend (frontend/) -------------------------------------------
    # Where the SPA is served; used for links in outgoing emails.
    frontend_url: Optional[str] = Field(default=None, alias="FRONTEND_URL")
    # Comma-separated origins allowed to call /api/* from the browser.
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")

    # --- Logging / observability --------------------------------------------
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    gchat_webhook: Optional[str] = Field(None, alias="GCHAT_WEBHOOK")
    sentry_dsn: Optional[str] = Field(None, alias="SENTRY_DSN")

    # --- OAuth login (Google today; add another client id + verifier in
    # app/routes/operations/auth_ops.py for Apple/others) --------------------
    google_oauth_client_id: Optional[str] = Field(None, alias="GOOGLE_OAUTH_CLIENT_ID")

    # --- Registration approval --------------------------------------------------
    # The key handed out to people who may register straight away; anyone
    # registering without it (or with a wrong one) is created "pending" until
    # the approver clicks the link emailed to them. Unset = everyone is pending.
    registration_key: Optional[str] = Field(default=None, alias="REGISTRATION_KEY")
    # Unset = approval requests aren't emailed to anyone.
    registration_approver_email: Optional[str] = Field(
        default=None, alias="REGISTRATION_APPROVER_EMAIL"
    )
    # Shown to pending users (sign-up popup and email) as who to contact.
    # Unset = the approver's address.
    registration_contact_email: Optional[str] = Field(
        default=None, alias="REGISTRATION_CONTACT_EMAIL"
    )

    # --- Feedback (app/routes/operations/feedback_ops.py) ------------------------
    # Where users' bug reports and improvement ideas are emailed.
    # Unset = the registration approver.
    feedback_email: Optional[str] = Field(default=None, alias="FEEDBACK_EMAIL")

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
    def supabase_connection_url(self) -> Optional[str]:
        if self.supabase_database_url:
            return self.supabase_database_url
        if not (self.supabase_project and self.supabase_region and self.supabase_password):
            return None
        return (
            "postgresql+psycopg2://postgres.{project}:{password}"
            "@{pooler}-{region}.pooler.supabase.com:{port}/{db}?sslmode=require"
        ).format(
            project=self.supabase_project,
            password=quote_plus(self.supabase_password),
            pooler=self.supabase_pooler,
            region=self.supabase_region,
            port=self.supabase_port,
            db=self.supabase_db,
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
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @computed_field  # type: ignore[misc]
    @property
    def effective_jwt_secret_key(self) -> str:
        return self.jwt_secret_key or self.secret_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
