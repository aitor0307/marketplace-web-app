from app.extensions import db
from app.models.mixins import CRUDMixin


class Listing(CRUDMixin, db.Model):
    __tablename__ = "listing"

    title = db.Column(db.String(100))
    price = db.Column(db.Float)
    condition = db.Column(db.String(10))
    body = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
