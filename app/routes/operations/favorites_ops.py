from flask import Blueprint, g, jsonify

from app.decorators.auth import jwt_verify
from app.decorators.docs import api_doc
from app.models import Listing, User
from app.routes.operations.listings_ops import serialize_listing

favorites_ops_bp = Blueprint("ops_favorites", __name__, url_prefix="/api/v1/favorites")


def add_favorite(user, listing_id):
    """Returns True when the listing was newly added."""
    return user.add_favorite(listing_id)


def remove_favorite(user, listing_id):
    """Returns True when the listing was in the user's favorites."""
    return user.remove_favorite(listing_id)


def get_favorite_listings(user):
    """The user's favorites, most recently added first. Ids of listings that
    have since been deleted are skipped."""
    ids = user.favorite_listing_ids
    if not ids:
        return []
    by_id = {listing.id: listing for listing in Listing.query.filter(Listing.id.in_(ids)).all()}
    return [by_id[i] for i in reversed(ids) if i in by_id]


@favorites_ops_bp.route("", methods=["GET"])
@api_doc("List the current user's favorite listings, most recently added first", tags=["favorites"])
@jwt_verify()
def list_favorites_operation():
    user = User.get_by_id(g.user_id)
    return jsonify(listings=[serialize_listing(listing) for listing in get_favorite_listings(user)])


@favorites_ops_bp.route("/<int:listing_id>", methods=["POST"])
@api_doc("Add a listing to the current user's favorites", tags=["favorites"])
@jwt_verify()
def add_favorite_operation(listing_id):
    if Listing.get_by_id(listing_id) is None:
        return jsonify(error="Listing not found"), 404
    user = User.get_by_id(g.user_id)
    created = add_favorite(user, listing_id)
    return (
        jsonify(created=created, favorite_listing_ids=user.favorite_listing_ids),
        201 if created else 200,
    )


@favorites_ops_bp.route("/<int:listing_id>", methods=["DELETE"])
@api_doc("Remove a listing from the current user's favorites", tags=["favorites"])
@jwt_verify()
def remove_favorite_operation(listing_id):
    user = User.get_by_id(g.user_id)
    removed = remove_favorite(user, listing_id)
    return jsonify(removed=removed, favorite_listing_ids=user.favorite_listing_ids)
