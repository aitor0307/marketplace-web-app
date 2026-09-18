from app.routes.operations.auth_ops import auth_ops_bp
from app.routes.operations.favorites_ops import favorites_ops_bp
from app.routes.operations.listings_ops import listings_ops_bp
from app.routes.operations.messages_ops import messages_ops_bp
from app.routes.operations.users_ops import users_ops_bp

operations_blueprints = (
    auth_ops_bp,
    users_ops_bp,
    listings_ops_bp,
    favorites_ops_bp,
    messages_ops_bp,
)
