from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required


def roles_required(*roles):
    """Require a valid JWT and, if roles are given, one of those roles.

    Usage:
        @roles_required()            # any authenticated user
        @roles_required("admin")     # admin only
    """

    def decorator(view_func):
        @wraps(view_func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            if roles:
                claims = get_jwt()
                if claims.get("role") not in roles:
                    return jsonify(error="Forbidden: insufficient role"), 403
            return view_func(*args, **kwargs)

        return wrapper

    return decorator
