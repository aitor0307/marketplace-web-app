"""Single place where every Flask extension is instantiated.

Extensions are created unbound here and wired to a concrete app inside
``create_app`` via ``init_app``. This is what lets the app factory build
more than one app instance (e.g. one per test) without extensions leaking
state between them.
"""
import redis
from flask_bootstrap import Bootstrap5
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "views_auth.login"
mail = Mail()
bootstrap = Bootstrap5()
moment = Moment()
jwt = JWTManager()


class RedisClient:
    """Thin lazy wrapper around a redis-py client.

    Nothing in the app talks to Redis yet, but the connection is fully
    configured so caching, rate limiting, or a vector index (RediSearch /
    redis-vector) can be added later without touching config or the
    factory again.
    """

    def __init__(self):
        self._client = None

    def init_app(self, app):
        self._client = redis.from_url(
            app.config["REDIS_URL"], decode_responses=True
        )
        app.extensions["redis"] = self._client

    @property
    def client(self):
        if self._client is None:
            raise RuntimeError("RedisClient.init_app(app) has not been called yet")
        return self._client

    def ping(self):
        try:
            return self.client.ping()
        except redis.exceptions.RedisError:
            return False


redis_client = RedisClient()
