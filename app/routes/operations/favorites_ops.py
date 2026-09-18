from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity

from app.decorators.auth import jwt_verify
from app.decorators.docs import api_doc
from app.models import Favorite, User

favorites_ops_bp = Blueprint("ops_favorites", __name__, url_prefix="/api/v1/favorites")


def add_favorite(user, listing_id):
    existing = Favorite.query.filter_by(listing_id=listing_id, user_id=user.id).first()
    if existing:
        return existing, False
    return Favorite.create(listing_id=listing_id, user_id=user.id), True


@favorites_ops_bp.route("/<int:listing_id>", methods=["POST"])
@api_doc("Add a listing to the current user's favorites", tags=["favorites"])
@jwt_verify()
def add_favorite_operation(listing_id):
    user = User.get_by_id(get_jwt_identity())
    favorite, created = add_favorite(user, listing_id)
    return jsonify(favorite=favorite.to_dict(), created=created), 201 if created else 200
