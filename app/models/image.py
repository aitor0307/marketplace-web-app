from app.extensions import db
from app.models.mixins import CRUDMixin


class Image(CRUDMixin, db.Model):
    __tablename__ = "image"

    name = db.Column(db.String(100))
    extension = db.Column(db.String(100))
    instance = db.Column(db.Integer)
    src = db.Column(db.String(100))
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"))
