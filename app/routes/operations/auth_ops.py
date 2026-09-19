"""Auth logic: registration and credential checks, plus the JWT API.

``register_user`` / ``authenticate_user`` are plain functions the view
blueprint calls directly for the session-based web login. The Flask routes
below wrap the same logic for API clients and hand back JWTs.
"""
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token

from app.decorators.docs import api_doc
from app.models import OAuthAccount, User
from app.schemas.auth import LoginPayload, OAuthLoginPayload, RegisterPayload

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


def verify_google_id_token(id_token_value):
    """Verify a Google-issued ID token and return the caller's identity.

    Raises on an invalid/expired token or a missing GOOGLE_OAUTH_CLIENT_ID
    (the audience every token must have been issued for); callers treat
    any exception here as "reject the login".
    """
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token as google_id_token

    client_id = current_app.config["GOOGLE_OAUTH_CLIENT_ID"]
    if not client_id:
        raise RuntimeError("GOOGLE_OAUTH_CLIENT_ID is not configured")

    claims = google_id_token.verify_oauth2_token(
        id_token_value, google_requests.Request(), audience=client_id
    )
    return {
        "provider_user_id": claims["sub"],
        "email": claims.get("email"),
        "name": claims.get("name"),
    }


# Every supported provider registers a verifier here: given the raw
# id_token string, return {"provider_user_id", "email", "name"} or raise.
# Apple (or anything else) is a matter of writing one more function with
# this shape and adding it to the registry - no other code changes.
OAUTH_VERIFIERS = {
    "google": verify_google_id_token,
}


def find_or_create_oauth_user(provider, provider_user_id, email, name):
    """Look up the user linked to this provider identity, creating both the
    user and the link on first sign-in. Returns (user, created)."""
    account = OAuthAccount.query.filter_by(
        provider=provider, provider_user_id=provider_user_id
    ).first()
    if account is not None:
        return account.user, False

    user = User.query.filter_by(email=email).first() if email else None
    created = user is None
    if created:
        user = User.create(name=name or (email or provider_user_id), email=email)

    OAuthAccount.create(
        provider=provider, provider_user_id=provider_user_id, email=email, user_id=user.id
    )
    return user, created


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


@auth_ops_bp.route("/oauth/login", methods=["POST"])
@api_doc(
    "Register or log in with a third-party provider's ID token (Google today)",
    tags=["auth"],
    auth=False,
)
def oauth_login_operation():
    payload = OAuthLoginPayload(**(request.get_json(silent=True) or {}))

    verifier = OAUTH_VERIFIERS.get(payload.provider)
    if verifier is None:
        return jsonify(error=f"Unsupported OAuth provider: {payload.provider}"), 400

    try:
        identity = verifier(payload.id_token)
    except Exception:
        return jsonify(error="Invalid or expired OAuth token"), 401

    user, created = find_or_create_oauth_user(
        provider=payload.provider,
        provider_user_id=identity["provider_user_id"],
        email=identity.get("email"),
        name=identity.get("name"),
    )
    return jsonify(user=user.to_dict(), **issue_tokens(user)), 201 if created else 200
