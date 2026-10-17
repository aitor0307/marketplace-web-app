import os
import uuid

from flask import Blueprint, current_app, g, jsonify, request

from app.decorators.auth import jwt_verify
from app.decorators.docs import api_doc
from app.models import Listing, User
from app.routes.operations.favorites_ops import get_favorite_listings
from app.routes.operations.listings_ops import serialize_listing
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


def remove_avatar_file(user):
    if user.avatar_src:
        path = os.path.join(current_app.config["AVATARS_FOLDER"], user.avatar_src)
        if os.path.exists(path):
            os.remove(path)


def save_avatar(user, image_file):
    """Store ``image_file`` as the user's avatar, replacing any previous one.
    Returns an error message, or None on success."""
    ext = os.path.splitext(image_file.filename)[1].lstrip(".").lower()
    if ext not in current_app.config["AVATAR_EXTENSIONS"]:
        allowed = ", ".join(sorted(current_app.config["AVATAR_EXTENSIONS"]))
        return "The avatar must be an image ({})".format(allowed)

    image_file.stream.seek(0, os.SEEK_END)
    size = image_file.stream.tell()
    image_file.stream.seek(0)
    max_bytes = current_app.config["MAX_AVATAR_BYTES"]
    if size > max_bytes:
        return "The avatar must be at most {} MB".format(max_bytes // (1024 * 1024))

    folder = current_app.config["AVATARS_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    # A new random name per upload, so browsers never show a cached old picture.
    location = "{}-{}.{}".format(user.id, uuid.uuid4().hex[:12], ext)
    image_file.save(os.path.join(folder, location))
    remove_avatar_file(user)
    user.update(avatar_src=location)
    return None


def delete_avatar(user):
    remove_avatar_file(user)
    return user.update(avatar_src=None)


def get_user_listings(user):
    return Listing.query.filter_by(user_id=user.id).order_by(Listing.timestamp.desc()).all()


def get_user_favorites(user):
    return get_favorite_listings(user)


@users_ops_bp.route("/<int:user_id>", methods=["GET"])
@api_doc("Fetch a user profile", tags=["users"], auth=False)
def get_user_operation(user_id):
    user = get_user(user_id)
    if user is None:
        return jsonify(error="User not found"), 404
    return jsonify(user=user.to_public_dict())


@users_ops_bp.route("/<int:user_id>", methods=["PUT"])
@api_doc("Update a user profile (self only)", tags=["users"], request_model=UpdateUserPayload)
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


@users_ops_bp.route("/<int:user_id>/avatar", methods=["PUT"])
@api_doc(
    "Upload your profile picture (self only)",
    description="A multipart 'avatar' file field: jpg, png, gif or webp, at most 5 MB.",
    tags=["users"],
)
@jwt_verify()
def upload_avatar_operation(user_id):
    if user_id != g.user_id:
        return jsonify(error="Forbidden: can only edit your own profile"), 403
    user = get_user(user_id)
    if user is None:
        return jsonify(error="User not found"), 404

    image_file = request.files.get("avatar")
    if not image_file or not image_file.filename:
        return jsonify(error="An image file is required"), 400
    error = save_avatar(user, image_file)
    if error:
        return jsonify(error=error), 400
    return jsonify(user=user.to_dict())


@users_ops_bp.route("/<int:user_id>/avatar", methods=["DELETE"])
@api_doc("Remove your profile picture (self only)", tags=["users"])
@jwt_verify()
def delete_avatar_operation(user_id):
    if user_id != g.user_id:
        return jsonify(error="Forbidden: can only edit your own profile"), 403
    user = get_user(user_id)
    if user is None:
        return jsonify(error="User not found"), 404
    delete_avatar(user)
    return jsonify(user=user.to_dict())


@users_ops_bp.route("/<int:user_id>/listings", methods=["GET"])
@api_doc("List a user's listings, newest first", tags=["users"], auth=False)
def get_user_listings_operation(user_id):
    user = get_user(user_id)
    if user is None:
        return jsonify(error="User not found"), 404
    return jsonify(listings=[serialize_listing(listing) for listing in get_user_listings(user)])


@users_ops_bp.route("/<int:user_id>/favorites", methods=["GET"])
@api_doc("List a user's favorite listings (self only)", tags=["users"])
@jwt_verify()
def get_user_favorites_operation(user_id):
    if user_id != g.user_id:
        return jsonify(error="Forbidden: can only view your own favorites"), 403
    user = get_user(user_id)
    if user is None:
        return jsonify(error="User not found"), 404
    return jsonify(listings=[serialize_listing(listing) for listing in get_user_favorites(user)])
