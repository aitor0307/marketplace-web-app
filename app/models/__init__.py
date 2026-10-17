"""Import every model so Alembic autogenerate and db.create_all() see them."""
from app.models.mixins import CRUDMixin
from app.models.user import User, ROLE_ADMIN, ROLE_USER, STATUS_ACTIVE, STATUS_PENDING
from app.models.listing import Listing
from app.models.image import Image
from app.models.favorite import Favorite
from app.models.message import Message
from app.models.oauth_account import OAuthAccount, PROVIDER_APPLE, PROVIDER_GOOGLE

__all__ = [
    "CRUDMixin",
    "User",
    "ROLE_ADMIN",
    "ROLE_USER",
    "STATUS_ACTIVE",
    "STATUS_PENDING",
    "Listing",
    "Image",
    "Favorite",
    "Message",
    "OAuthAccount",
    "PROVIDER_GOOGLE",
    "PROVIDER_APPLE",
]
