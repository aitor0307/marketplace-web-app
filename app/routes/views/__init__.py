from app.routes.views.auth import views_auth_bp
from app.routes.views.favorites import views_favorites_bp
from app.routes.views.listings import views_listings_bp
from app.routes.views.messages import views_messages_bp
from app.routes.views.users import views_users_bp

view_blueprints = (
    views_listings_bp,
    views_auth_bp,
    views_users_bp,
    views_messages_bp,
    views_favorites_bp,
)
