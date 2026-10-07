import os

from flask import Blueprint, current_app, g, jsonify, request, url_for
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


def get_listing_images(listing_id):
    """All of a listing's images in upload order; the first one is the cover."""
    return Image.query.filter_by(listing_id=listing_id).order_by(Image.id).all()


def get_listing_image(listing_id):
    return Image.query.filter_by(listing_id=listing_id).order_by(Image.id).first()


def listing_image_url(image):
    if image is None or not image.src:
        return None
    return url_for("static", filename="listing_images/{}".format(image.src))


def serialize_listing(listing, images=None):
    """Listing JSON for API clients: the row plus what the views pull in
    alongside it (images, author card, tags). ``image_url`` stays as the
    cover so clients that only show one picture keep working."""
    images = images if images is not None else get_listing_images(listing.id)
    image_urls = [url for url in map(listing_image_url, images) if url]
    author = listing.author
    data = listing.to_dict()
    data["image_url"] = image_urls[0] if image_urls else None
    data["image_urls"] = image_urls
    data["tags"] = (listing.external_data or {}).get("tags") or []
    data["author"] = author.to_summary() if author is not None else None
    return data


def save_listing_image(listing_id, image_file):
    # TODO set to store to a secure bucket not to filesystem if set up
    # Maybe handle it directly in the Storage class, where we can set to filesystem or bucket.
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


def save_listing_images(listing_id, image_files):
    return [save_listing_image(listing_id, image_file) for image_file in image_files]


def create_listing(user, title, body, condition, price, image_files, tags):
    listing = Listing.create(
        title=title, body=body, condition=condition, price=price, user_id=user.id, external_data={"tags": tags}
    )
    images = save_listing_images(listing.id, image_files)
    return listing, images


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
    return jsonify(listings=[serialize_listing(listing) for listing in listings])


@listings_ops_bp.route("/<int:listing_id>", methods=["GET"])
@api_doc("Fetch a single listing", tags=["listings"], auth=False)
def get_listing_operation(listing_id):
    listing = get_listing(listing_id)
    if listing is None:
        return jsonify(error="Listing not found"), 404
    return jsonify(listing=serialize_listing(listing))


@listings_ops_bp.route("", methods=["POST"])
@api_doc(
    "Create a listing with one or more image uploads",
    description=(
        "Also requires one or more multipart 'images' file fields alongside these text "
        "fields (the first one is the cover). A single 'image' field is still accepted."
    ),
    tags=["listings"],
    request_model=CreateListingPayload,
    request_content_type="multipart/form-data",
)
@jwt_verify()
def create_listing_operation():
    user = User.get_by_id(g.user_id)
    if not user.is_approved:
        return jsonify(error="Your account is pending approval"), 403
    # Tags arrive as a repeated multipart field; to_dict() would keep only
    # the first one, as a string, so read them as a list explicitly.
    payload = CreateListingPayload(
        **{**request.form.to_dict(), "tags": request.form.getlist("tags")}
    )

    # Images aren't representable as pydantic fields: they're file streams,
    # not JSON/form scalar data, so they're read separately. 'images' is
    # repeated once per file; the legacy single 'image' field still works.
    image_files = [
        image_file
        for image_file in request.files.getlist("images") + request.files.getlist("image")
        if image_file and image_file.filename
    ]
    if not image_files:
        return jsonify(error="An image file is required"), 400
    max_images = current_app.config["MAX_LISTING_IMAGES"]
    if len(image_files) > max_images:
        return jsonify(error="A listing can have at most {} images".format(max_images)), 400

    listing, images = create_listing(
        user=user,
        title=payload.title,
        body=payload.body,
        condition=payload.condition,
        price=payload.price,
        image_files=image_files,
        tags=payload.tags
    )
    return jsonify(
        listing=serialize_listing(listing, images), images=[image.to_dict() for image in images]
    ), 201


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
