import re
import traceback
from functools import wraps

from flask import g
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from jwt import ExpiredSignatureError

from app.utils.logger import logger


def jwt_verify(roles=[".*"], is_2fa=False):
    """
    Custom decorator to extend jwt_required() to check for roles.
    ADMIN is implicitly granted access to every route, unless the route is
    exclusively for SUPER_ADMIN.
    :param roles: List of roles required to access the route
    """
    allowed_roles = list(roles)
    if allowed_roles != ["SUPER_ADMIN"] and "ADMIN" not in allowed_roles:
        allowed_roles.append("ADMIN")

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Lazy import: app.models pulls in the ORM models, so importing it
            # at module top would be circular during app package init.
            from app.models.api_base import ResponseFactory
            try:
                verify_jwt_in_request()

                def role_allowed(role_to_check: str, allowed_roles: list[str]) -> bool:
                    return any(bool(re.fullmatch(pattern, role_to_check)) for pattern in allowed_roles)

                jwt_claims = get_jwt()
                if not role_allowed(jwt_claims['role'], allowed_roles):
                    return ResponseFactory.forbidden(f"Access denied. Required roles: {allowed_roles}")

                if is_2fa:
                    if 'init_token' not in jwt_claims:
                        return ResponseFactory.forbidden("Invalid token. 2FA required.")

                g.jwt_claims = jwt_claims
                g.company_id = jwt_claims.get('company_id')
                g.role = jwt_claims.get('role')
                g.user_id = jwt_claims.get('user_id')
                g.sub = jwt_claims.get('sub', None)
                return fn(*args, **kwargs)
            except ExpiredSignatureError:
                return ResponseFactory.bad_request("Token has expired!")
            except Exception as e:
                traceback.print_exc()
                logger.error(f"[SECURITY] JWT Exception: {e}")
                logger.catch_exception(e)
                return ResponseFactory.bad_request(f"JWT Exception: {e}")
        return wrapper
    return decorator
