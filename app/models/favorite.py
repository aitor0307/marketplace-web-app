from app.extensions import db
from app.models.mixins import CRUDMixin


class Favorite(CRUDMixin, db.Model):
    __tablename__ = "favorite"

    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
