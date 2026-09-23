from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.forms import FilterForm, ListingForm
from app.models import Image
from app.routes.operations.listings_ops import (
    create_listing,
    delete_listing,
    filter_listings,
    get_listing,
    get_listing_image,
)

views_listings_bp = Blueprint("views_listings", __name__)


@views_listings_bp.route("/", methods=["GET", "POST"])
@views_listings_bp.route("/index", methods=["GET", "POST"])
def index():
    form = FilterForm()
    if form.validate_on_submit():
        listings = filter_listings(
            condition=form.condition.data,
            price_min=form.price_min.data,
            price_max=form.price_max.data,
        )
    else:
        listings = filter_listings()

    images = {listing.id: get_listing_image(listing.id) for listing in listings}
    users = {listing.id: listing.author for listing in listings}
    return render_template(
        "index.html",
        title="Listings",
        listings=listings,
        images=images,
        users=users,
        user_info=True,
        form=form,
    )


@views_listings_bp.route("/new_listing", methods=["GET", "POST"])
@login_required
def new_listing():
    form = ListingForm()
    if form.validate_on_submit():
        listing, _image = create_listing(
            user=current_user,
            title=form.title.data,
            body=form.body.data,
            condition=form.condition.data,
            price=form.price.data,
            image_file=form.image.data,
        )
        flash("Listing created")
        return redirect(url_for("views_listings.listing_detail", listing_id=listing.id))
    return render_template("new_listing.html", title="Create New Listing", form=form)


@views_listings_bp.route("/listing/<int:listing_id>")
def listing_detail(listing_id):
    listing = get_listing(listing_id)
    if listing is None:
        abort(404)
    image = Image.query.filter_by(listing_id=listing.id).first()
    return render_template(
        "listing.html",
        listing=listing,
        title="View Listing",
        image=image,
        user=listing.author,
        current_user=current_user,
    )


@views_listings_bp.route("/delete_listing/<int:listing_id>")
@login_required
def delete_listing_view(listing_id):
    _listing, error = delete_listing(current_user, listing_id)
    if error:
        flash(error)
        return redirect(url_for("views_listings.listing_detail", listing_id=listing_id))
    flash("Listing deleted")
    return redirect(url_for("views_listings.index"))
