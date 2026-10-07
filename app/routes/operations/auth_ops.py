"""Auth logic: registration and credential checks, plus the JWT API.

``register_user`` / ``authenticate_user`` are plain functions the view
blueprint calls directly for the session-based web login. The Flask routes
below wrap the same logic for API clients and hand back JWTs.

Registration approval: a user who registers with the configured
REGISTRATION_KEY is active right away. Anyone else (no key, a wrong key, or
a first-time OAuth sign-in) is created "pending" - they can log in but not
publish listings - and REGISTRATION_APPROVER_EMAIL gets a signed link to
approve them.
"""
import hmac

from flask import Blueprint, current_app, g, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from markupsafe import escape

from app.decorators.auth import jwt_verify
from app.decorators.docs import api_doc
from app.email import send_email
from app.models import STATUS_ACTIVE, STATUS_PENDING, OAuthAccount, User
from app.schemas.auth import LoginPayload, OAuthLoginPayload, RegisterPayload
from app.schemas.common import AuthResponse
from app.utils.logger import logger
from tools.apidocs import json_response, pydantic_response, responses

auth_ops_bp = Blueprint("ops_auth", __name__, url_prefix="/api/v1/auth")

APPROVAL_TOKEN_SALT = "registration-approval"


def registration_key_matches(registration_key):
    expected = current_app.config.get("REGISTRATION_KEY")
    if not expected or not registration_key:
        return False
    return hmac.compare_digest(registration_key.strip().encode(), expected.encode())


def make_approval_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=APPROVAL_TOKEN_SALT)


def approval_token_for(user):
    return make_approval_serializer().dumps({"user_id": user.id})


def user_for_approval_token(token):
    """The user an approval link was issued for, or (None, error) when the
    link was tampered with, has expired, or the user no longer exists."""
    try:
        data = make_approval_serializer().loads(
            token, max_age=current_app.config["REGISTRATION_APPROVAL_MAX_AGE"]
        )
    except SignatureExpired:
        return None, "This approval link has expired"
    except BadSignature:
        return None, "Invalid approval link"
    user = User.get_by_id(data.get("user_id"))
    if user is None:
        return None, "User not found"
    return user, None


def approval_url_for(user):
    # The link only opens a confirmation page in the React app; the approval
    # itself is a POST from there, so mail scanners prefetching the link
    # can't approve anyone.
    base_url = current_app.config.get("FRONTEND_URL") or current_app.config["HOST"]
    return "{}/approvals/{}".format(base_url.rstrip("/"), approval_token_for(user))


def send_approval_request(user):
    try:
        approval_url = approval_url_for(user)
        html = (
            "<p>A new user registered on Marketplace without a valid registration key "
            "and is waiting for approval:</p>"
            "<ul><li>Name: {name}</li><li>Email: {email}</li><li>Location: {location}</li></ul>"
            "<p><a href='{approval_url}'>Review and approve this user</a></p>"
        ).format(
            name=escape(user.name),
            email=escape(user.email),
            location=escape(", ".join(filter(None, [user.city, user.state]))),
            approval_url=escape(approval_url),
        )
        send_email(
            "New Marketplace user pending approval: {}".format(user.name),
            current_app.config["MAIL_USERNAME"],
            [current_app.config["REGISTRATION_APPROVER_EMAIL"]],
            html,
            html,
        )
    except Exception as e:
        # The user is already stored, so a mail failure must not fail the registration.
        logger.error(f"Failed to send the approval request for user {user.id}")
        logger.catch_exception(e)


def register_user(name, email, password, state, city, registration_key=None):
    status = STATUS_ACTIVE if registration_key_matches(registration_key) else STATUS_PENDING
    user = User.create(
        name=name, email=email, state=state, city=city, status=status, commit=False
    )
    user.set_password(password)
    user.save()
    if not user.is_approved:
        send_approval_request(user)
    return user


def approve_user(user):
    if not user.is_approved:
        user.approve()
    return user


def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return None
    return user


def _token_claims(user):
    return {"role": user.role, "user_id": user.id}


def issue_tokens(user):
    claims = _token_claims(user)
    return {
        "access_token": create_access_token(identity=str(user.id), additional_claims=claims),
        "refresh_token": create_refresh_token(identity=str(user.id), additional_claims=claims),
    }


def issue_access_token(user):
    return create_access_token(identity=str(user.id), additional_claims=_token_claims(user))


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
        # No registration key on this path, so new OAuth users need approval too.
        user = User.create(
            name=name or (email or provider_user_id), email=email, status=STATUS_PENDING
        )
        send_approval_request(user)

    OAuthAccount.create(
        provider=provider, provider_user_id=provider_user_id, email=email, user_id=user.id
    )
    return user, created


@auth_ops_bp.route("/register", methods=["POST"])
@api_doc(
    "Register a new user",
    description=(
        "With the right 'registration_key' the user is active right away; otherwise "
        "they are created with status 'pending' and an approval link is emailed."
    ),
    tags=["auth"],
    auth=False,
    request_model=RegisterPayload,
    responses=responses(
        created=pydantic_response(AuthResponse, "Newly created user + JWT tokens"),
        conflict=json_response({"type": "object"}, "Email already registered"),
    ),
)
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
        registration_key=payload.registration_key,
    )
    return jsonify(user=user.to_dict(), **issue_tokens(user)), 201


@auth_ops_bp.route("/login", methods=["POST"])
@api_doc(
    "Exchange credentials for a JWT access/refresh token pair",
    tags=["auth"],
    auth=False,
    request_model=LoginPayload,
    responses=responses(
        ok=pydantic_response(AuthResponse, "Authenticated user + JWT tokens"),
        unauthorized=json_response({"type": "object"}, "Invalid email or password"),
    ),
)
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
    request_model=OAuthLoginPayload,
    responses=responses(
        ok=pydantic_response(AuthResponse, "Existing user, now linked/re-authenticated"),
        created=pydantic_response(AuthResponse, "Newly created user, linked on first sign-in"),
        bad_request=json_response({"type": "object"}, "Unsupported provider"),
        unauthorized=json_response({"type": "object"}, "Invalid or expired OAuth token"),
    ),
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


@auth_ops_bp.route("/me", methods=["GET"])
@api_doc(
    "Fetch the user the access token belongs to",
    tags=["auth"],
    responses=responses(
        ok=json_response({"type": "object"}, "The authenticated user"),
        not_found=json_response({"type": "object"}, "User no longer exists"),
    ),
)
@jwt_verify()
def me_operation():
    user = User.get_by_id(g.user_id)
    if user is None:
        return jsonify(error="User not found"), 404
    return jsonify(user=user.to_dict())


@auth_ops_bp.route("/refresh", methods=["POST"])
@api_doc(
    "Exchange a refresh token (sent as the Bearer token) for a new access token",
    tags=["auth"],
    responses=responses(
        ok=json_response({"type": "object"}, "A fresh access token"),
        not_found=json_response({"type": "object"}, "User no longer exists"),
    ),
)
@jwt_verify(refresh=True)
def refresh_operation():
    # Re-read the user so role changes since the last login land in the new token.
    user = User.get_by_id(g.user_id)
    if user is None:
        return jsonify(error="User not found"), 404
    return jsonify(access_token=issue_access_token(user))


@auth_ops_bp.route("/approvals/<token>", methods=["GET"])
@api_doc(
    "Look up the user an emailed approval link is for",
    tags=["auth"],
    auth=False,
    responses=responses(
        ok=json_response({"type": "object"}, "The user awaiting (or already given) approval"),
        bad_request=json_response({"type": "object"}, "Invalid or expired approval link"),
    ),
)
def get_approval_operation(token):
    user, error = user_for_approval_token(token)
    if error:
        return jsonify(error=error), 400
    return jsonify(user=user.to_dict())


@auth_ops_bp.route("/approvals/<token>", methods=["POST"])
@api_doc(
    "Approve the user an emailed approval link is for",
    description="The signed token is the authorization; approving twice is a no-op.",
    tags=["auth"],
    auth=False,
    responses=responses(
        ok=json_response({"type": "object"}, "The now active user"),
        bad_request=json_response({"type": "object"}, "Invalid or expired approval link"),
    ),
)
def approve_operation(token):
    user, error = user_for_approval_token(token)
    if error:
        return jsonify(error=error), 400
    return jsonify(user=approve_user(user).to_dict())
