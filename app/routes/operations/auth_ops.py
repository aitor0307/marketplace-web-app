"""Auth logic: registration and credential checks, plus the JWT API.

``register_user`` / ``authenticate_user`` are plain functions the view
blueprint calls directly for the session-based web login. The Flask routes
below wrap the same logic for API clients and hand back JWTs.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token

from app.decorators.docs import api_doc
from app.models import User
from app.schemas.auth import LoginPayload, RegisterPayload

auth_ops_bp = Blueprint("ops_auth", __name__, url_prefix="/api/v1/auth")


def register_user(name, email, password, state, city):
    user = User.create(name=name, email=email, state=state, city=city, commit=False)
    user.set_password(password)
    user.save()
    return user


def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return None
    return user


def issue_tokens(user):
    claims = {"role": user.role, "user_id": user.id}
    return {
        "access_token": create_access_token(identity=str(user.id), additional_claims=claims),
        "refresh_token": create_refresh_token(identity=str(user.id), additional_claims=claims),
    }


@auth_ops_bp.route("/register", methods=["POST"])
@api_doc("Register a new user", tags=["auth"], auth=False)
def register_operation():
    # Constructing the model from the raw body is the validation: an
    # invalid payload raises pydantic.ValidationError here, which
    # app.errors' errorhandler turns into a 400.
    payload = RegisterPayload(**(request.get_json(silent=True) or {}))

    if User.query.filter_by(email=payload.email).first() is not None:
        return jsonify(error="Email already registered"), 409

    user = register_user(
        name=payload.name,
        email=payload.email,
        password=payload.password,
        state=payload.state,
        city=payload.city,
    )
    return jsonify(user=user.to_dict(), **issue_tokens(user)), 201


@auth_ops_bp.route("/login", methods=["POST"])
@api_doc("Exchange credentials for a JWT access/refresh token pair", tags=["auth"], auth=False)
def login_operation():
    payload = LoginPayload(**(request.get_json(silent=True) or {}))
    user = authenticate_user(payload.email, payload.password)
    if user is None:
        return jsonify(error="Invalid email or password"), 401
    return jsonify(user=user.to_dict(), **issue_tokens(user))
