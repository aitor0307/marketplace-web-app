from app.extensions import db
from app.models.mixins import CRUDMixin

PROVIDER_GOOGLE = "google"
PROVIDER_APPLE = "apple"


class OAuthAccount(CRUDMixin, db.Model):
    """One row per (provider, provider account) a user has signed in with.

    A user can link more than one provider (Google and Apple, say), so the
    foreign key lives here pointing at User, not the other way around.
    """

    __tablename__ = "oauth_account"
    __table_args__ = (
        db.UniqueConstraint("provider", "provider_user_id", name="uq_oauth_account_identity"),
    )

    provider = db.Column(db.String(20), nullable=False)
    provider_user_id = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
