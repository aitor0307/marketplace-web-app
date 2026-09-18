"""Import every model so Alembic autogenerate and db.create_all() see them."""
from app.models.mixins import CRUDMixin
from app.models.user import User, ROLE_ADMIN, ROLE_USER
from app.models.listing import Listing
from app.models.image import Image
from app.models.favorite import Favorite

__all__ = [
    "CRUDMixin",
    "User",
    "ROLE_ADMIN",
    "ROLE_USER",
    "Listing",
    "Image",
    "Favorite",
]
