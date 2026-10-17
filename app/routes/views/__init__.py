"""DEPRECATED: server-rendered Jinja views.

Superseded by the React app in frontend/, which talks to the JSON API in
app/routes/operations. Kept mounted (and working) until the frontend fully
replaces them; do not add features here. Every response is tagged with a
``Deprecation`` header by app.decorators.deprecation.
"""
from app.decorators.deprecation import deprecate_blueprint
from app.routes.views.auth import views_auth_bp
from app.routes.views.favorites import views_favorites_bp
from app.routes.views.listings import views_listings_bp
from app.routes.views.messages import views_messages_bp
from app.routes.views.users import views_users_bp

# Jinja endpoint -> React route that replaces it (see frontend/src/config/constants.ts).
SPA_SUCCESSORS = {
    "views_listings.index": "/",
    "views_listings.new_listing": "/listings/new",
    "views_listings.listing_detail": "/listings/{listing_id}",
    "views_listings.delete_listing_view": "/listings/{listing_id}",
    "views_auth.login": "/login",
    "views_auth.register": "/register",
    "views_users.view_user": "/users/{user_id}",
    "views_users.edit_profile": "/profile/edit",
    "views_messages.message": "/users/{user_id}/message",
    "views_favorites.favorite": "/listings/{listing_id}",
}

view_blueprints = tuple(
    deprecate_blueprint(blueprint, SPA_SUCCESSORS)
    for blueprint in (
        views_listings_bp,
        views_auth_bp,
        views_users_bp,
        views_messages_bp,
        views_favorites_bp,
    )
)
