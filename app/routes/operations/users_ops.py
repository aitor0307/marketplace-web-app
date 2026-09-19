from flask import Blueprint, g, jsonify, request

from app.decorators.auth import jwt_verify
from app.decorators.docs import api_doc
from app.models import Favorite, Listing, User
from app.schemas.users import UpdateUserPayload

users_ops_bp = Blueprint("ops_users", __name__, url_prefix="/api/v1/users")


def get_user(user_id):
    return User.get_by_id(user_id)


def update_user(user, name=None, email=None, state=None, city=None):
    updates = {
        k: v
        for k, v in {"name": name, "email": email, "state": state, "city": city}.items()
        if v is not None
    }
    return user.update(**updates)


def get_user_listings(user):
    return Listing.query.filter_by(user_id=user.id).order_by(Listing.timestamp.desc()).all()


def get_user_favorites(user):
    favorite_ids = [f.listing_id for f in Favorite.query.filter_by(user_id=user.id).all()]
    if not favorite_ids:
        return []
    return Listing.query.filter(Listing.id.in_(favorite_ids)).all()


@users_ops_bp.route("/<int:user_id>", methods=["GET"])
@api_doc("Fetch a user profile", tags=["users"], auth=False)
def get_user_operation(user_id):
    user = get_user(user_id)
    if user is None:
        return jsonify(error="User not found"), 404
    return jsonify(user=user.to_dict())


@users_ops_bp.route("/<int:user_id>", methods=["PUT"])
@api_doc("Update a user profile (self only)", tags=["users"])
@jwt_verify()
def update_user_operation(user_id):
    if user_id != g.user_id:
        return jsonify(error="Forbidden: can only edit your own profile"), 403
    user = get_user(user_id)
    if user is None:
        return jsonify(error="User not found"), 404

    payload = UpdateUserPayload(**(request.get_json(silent=True) or {}))
    update_user(user, **payload.model_dump(exclude_none=True))
    return jsonify(user=user.to_dict())
