from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms import EditProfileForm
from app.routes.operations.listings_ops import get_listing_image
from app.routes.operations.users_ops import get_user, get_user_favorites, get_user_listings, update_user

views_users_bp = Blueprint("views_users", __name__)


@views_users_bp.route("/user/<int:user_id>")
def view_user(user_id):
    user = get_user(user_id)
    if user is None:
        abort(404)
    listings = get_user_listings(user)
    favorites = get_user_favorites(user) if user == current_user else []
    images = {listing.id: get_listing_image(listing.id) for listing in listings}
    return render_template(
        "user.html",
        user=user,
        listings=listings,
        images=images,
        title="View Profile",
        user_info=False,
        favorites=favorites,
    )


@views_users_bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        update_user(
            current_user,
            name=form.name.data,
            email=form.email.data,
            state=form.state.data,
            city=form.city.data,
        )
        flash("Profile updated")
        return redirect(url_for("views_users.view_user", user_id=current_user.id))
    elif request.method == "GET":
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.state.data = current_user.state
        form.city.data = current_user.city
    return render_template("edit_profile.html", title="Edit Profile", form=form)
