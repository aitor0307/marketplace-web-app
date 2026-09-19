import os

from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.utils import secure_filename

from app.decorators.auth import jwt_verify
from app.decorators.docs import api_doc
from app.models import Image, Listing, User
from app.schemas.listings import CreateListingPayload, ListListingsQuery
from tools.apidocs import pydantic_query_params

listings_ops_bp = Blueprint("ops_listings", __name__, url_prefix="/api/v1/listings")


def filter_listings(condition=None, price_min=None, price_max=None):
    query = Listing.query
    if condition:
        query = query.filter(Listing.condition == condition)
    if price_min is not None:
        query = query.filter(Listing.price >= price_min)
    if price_max is not None:
        query = query.filter(Listing.price <= price_max)
    return query.order_by(Listing.timestamp.desc()).all()


def get_listing(listing_id):
    return Listing.get_by_id(listing_id)


def get_listing_image(listing_id):
    return Image.query.filter_by(listing_id=listing_id).first()


def save_listing_image(listing_id, image_file):
    filename, ext = os.path.splitext(secure_filename(image_file.filename))
    ext = ext.lstrip(".")
    instance = 0
    existing = (
        Image.query.filter_by(name=filename).order_by(Image.instance.desc()).first()
    )
    if existing and existing.instance is not None:
        instance = existing.instance + 1

    location = "{}{}.{}".format(filename, instance, ext)
    image_file.save(os.path.join(current_app.config["IMAGES_FOLDER"], location))
    return Image.create(
        name=filename, extension=ext, instance=instance, src=location, listing_id=listing_id
    )


def create_listing(user, title, body, condition, price, image_file):
    listing = Listing.create(
        title=title, body=body, condition=condition, price=price, user_id=user.id
    )
    image = save_listing_image(listing.id, image_file)
    return listing, image


def delete_listing(user, listing_id):
    listing = get_listing(listing_id)
    if listing is None:
        return None, "Listing not found"
    if listing.user_id != user.id:
        return None, "You can only delete listings you authored"
    Image.query.filter_by(listing_id=listing_id).delete()
    listing.delete()
    return listing, None


@listings_ops_bp.route("", methods=["GET"])
@api_doc(
    "List listings, optionally filtered by condition/price range",
    tags=["listings"],
    auth=False,
    parameters=pydantic_query_params(ListListingsQuery),
)
def list_listings_operation():
    payload = ListListingsQuery(**request.args.to_dict())
    listings = filter_listings(
        condition=payload.condition, price_min=payload.price_min, price_max=payload.price_max
    )
    return jsonify(listings=[listing.to_dict() for listing in listings])


@listings_ops_bp.route("/<int:listing_id>", methods=["GET"])
@api_doc("Fetch a single listing", tags=["listings"], auth=False)
def get_listing_operation(listing_id):
    listing = get_listing(listing_id)
    if listing is None:
        return jsonify(error="Listing not found"), 404
    return jsonify(listing=listing.to_dict())


@listings_ops_bp.route("", methods=["POST"])
@api_doc(
    "Create a listing with an image upload",
    description="Also requires a multipart 'image' file field alongside these text fields.",
    tags=["listings"],
    request_model=CreateListingPayload,
    request_content_type="multipart/form-data",
)
@jwt_verify()
def create_listing_operation():
    user = User.get_by_id(g.user_id)
    payload = CreateListingPayload(**request.form.to_dict())

    # The image itself isn't representable as a pydantic field: it's a
    # file stream, not JSON/form scalar data, so it's read separately.
    image_file = request.files.get("image")
    if image_file is None:
        return jsonify(error="An image file is required"), 400

    listing, image = create_listing(
        user=user,
        title=payload.title,
        body=payload.body,
        condition=payload.condition,
        price=payload.price,
        image_file=image_file,
    )
    return jsonify(listing=listing.to_dict(), image=image.to_dict()), 201


@listings_ops_bp.route("/<int:listing_id>", methods=["DELETE"])
@api_doc("Delete a listing you authored", tags=["listings"])
@jwt_verify()
def delete_listing_operation(listing_id):
    user = User.get_by_id(g.user_id)
    listing, error = delete_listing(user, listing_id)
    if error:
        status = 404 if listing is None and error == "Listing not found" else 403
        return jsonify(error=error), status
    return jsonify(deleted=True)
