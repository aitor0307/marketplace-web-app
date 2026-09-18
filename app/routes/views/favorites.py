from flask import Blueprint, flash, redirect, url_for
from flask_login import current_user, login_required

from app.routes.operations.favorites_ops import add_favorite

views_favorites_bp = Blueprint("views_favorites", __name__)


@views_favorites_bp.route("/favorite/<int:listing_id>")
@login_required
def favorite(listing_id):
    _favorite, created = add_favorite(current_user, listing_id)
    flash("Added to favorites" if created else "Already in your favorites")
    return redirect(url_for("views_listings.listing_detail", listing_id=listing_id))
