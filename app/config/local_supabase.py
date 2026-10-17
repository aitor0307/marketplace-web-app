from .base import Config, settings


class LocalSupabaseConfig(Config):
    """Local development against the Supabase Postgres database."""

    ENV = "local_supabase"
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = settings.supabase_connection_url
    # Supabase's pooler drops idle connections, so recycle before it does.
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 300}

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        if not app.config.get("SQLALCHEMY_DATABASE_URI"):
            missing = [
                name
                for name, value in (
                    ("SUPABASE_PROJECT", settings.supabase_project),
                    ("SUPABASE_REGION", settings.supabase_region),
                    ("SUPABASE_PASSWORD", settings.supabase_password),
                )
                if not value
            ]
            raise RuntimeError(
                "local_supabase config needs SUPABASE_DATABASE_URL or these unset/empty "
                "variables: {}".format(", ".join(missing))
            )
