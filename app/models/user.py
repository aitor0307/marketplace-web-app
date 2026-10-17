from hashlib import md5

from flask import url_for
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login
from app.models.mixins import CRUDMixin

ROLE_USER = "USER"
ROLE_ADMIN = "ADMIN"

# Account approval, unrelated to ``state`` (the user's province).
STATUS_ACTIVE = "active"
STATUS_PENDING = "pending"

# Key in ``external_data`` holding the user's favorite listing ids, oldest first.
FAVORITE_LISTING_IDS_KEY = "favorite_listing_ids"


class User(UserMixin, CRUDMixin, db.Model):
    __tablename__ = "user"

    name = db.Column(db.String(30))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    state = db.Column(db.String(50))  # province, see app/schemas/locations.py
    city = db.Column(db.String(50))
    role = db.Column(db.String(20), default=ROLE_USER, nullable=False)
    status = db.Column(
        db.String(20), default=STATUS_ACTIVE, server_default=STATUS_ACTIVE, nullable=False
    )
    last_seen = db.Column(db.DateTime)
    # Uploaded profile picture, a file in AVATARS_FOLDER; None = generated identicon.
    avatar_src = db.Column(db.String(100))

    listings = db.relationship("Listing", backref="author", lazy="dynamic")
    oauth_accounts = db.relationship("OAuthAccount", backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # An OAuth-only user (Google/Apple sign-in, no password set) has no
        # hash to compare against.
        return bool(self.password_hash) and check_password_hash(self.password_hash, password)

    def avatar(self, size):
        if self.avatar_src:
            return url_for("static", filename="avatars/{}".format(self.avatar_src))
        # Hashed from the (public) name, never the email: a Gravatar hash of
        # the email lets anyone confirm a guessed address. f=y always draws
        # the identicon, so it can't match someone's real Gravatar either.
        seed = (self.name or str(self.id)).strip().lower()
        digest = md5(seed.encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&f=y&s={}".format(digest, size)

    def has_role(self, role):
        return self.role == role

    @property
    def is_approved(self):
        # Not flask-login's ``is_active``: pending users may still log in,
        # they just can't publish listings until approved.
        return self.status == STATUS_ACTIVE

    def approve(self):
        return self.update(status=STATUS_ACTIVE)

    @property
    def favorite_listing_ids(self):
        return list((self.external_data or {}).get(FAVORITE_LISTING_IDS_KEY, []))

    def is_favorite(self, listing_id):
        return listing_id in self.favorite_listing_ids

    def add_favorite(self, listing_id):
        """Returns False when the listing was already a favorite."""
        ids = self.favorite_listing_ids
        if listing_id in ids:
            return False
        self._set_favorite_listing_ids(ids + [listing_id])
        return True

    def remove_favorite(self, listing_id):
        """Returns False when the listing wasn't a favorite."""
        ids = self.favorite_listing_ids
        if listing_id not in ids:
            return False
        self._set_favorite_listing_ids([i for i in ids if i != listing_id])
        return True

    def _set_favorite_listing_ids(self, ids):
        # A new dict, not an in-place edit: the JSON column doesn't track
        # mutations, so SQLAlchemy only notices a reassignment.
        self.update(external_data={**(self.external_data or {}), FAVORITE_LISTING_IDS_KEY: ids})

    def to_dict(self):
        # CRUDMixin.to_dict dumps every column; the password hash must never
        # leave the server, and API clients need the avatar the views build.
        data = super().to_dict()
        data.pop("password_hash", None)
        data["avatar_url"] = self.avatar_url()
        return data

    def avatar_url(self, size=128):
        return self.avatar(size)

    def to_summary(self):
        """The author card embedded in listings and messages."""
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "avatar_url": self.avatar_url(),
        }

    def to_public_dict(self):
        """What anyone may see of another user's profile: never their email,
        role or approval status (to_dict is only for the user themselves)."""
        data = self.to_summary()
        data["last_seen"] = self.last_seen
        return data


@login.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
