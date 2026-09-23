from hashlib import md5

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login
from app.models.mixins import CRUDMixin

ROLE_USER = "USER"
ROLE_ADMIN = "ADMIN"


class User(UserMixin, CRUDMixin, db.Model):
    __tablename__ = "user"

    name = db.Column(db.String(30))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    state = db.Column(db.String(20))
    city = db.Column(db.String(50))
    role = db.Column(db.String(20), default=ROLE_USER, nullable=False)
    last_seen = db.Column(db.DateTime)

    listings = db.relationship("Listing", backref="author", lazy="dynamic")
    oauth_accounts = db.relationship("OAuthAccount", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # An OAuth-only user (Google/Apple sign-in, no password set) has no
        # hash to compare against.
        return bool(self.password_hash) and check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(digest, size)

    def has_role(self, role):
        return self.role == role


@login.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
