from app.extensions import db
from app.models.mixins import CRUDMixin


class Message(CRUDMixin, db.Model):
    __tablename__ = "message"

    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"), nullable=True, index=True)
    subject = db.Column(db.String(140), nullable=False)
    body = db.Column(db.String(1000), nullable=False)

    sender = db.relationship("User", foreign_keys=[sender_id])
    recipient = db.relationship("User", foreign_keys=[recipient_id])
    listing = db.relationship("Listing")
