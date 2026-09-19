import pytest

from app.routes.operations import auth_ops


@pytest.fixture
def fake_google_verifier(monkeypatch):
    def _install(claims):
        monkeypatch.setitem(auth_ops.OAUTH_VERIFIERS, "google", lambda id_token: claims)

    return _install


def test_oauth_login_creates_user_and_links_account(client, fake_google_verifier, db):
    fake_google_verifier(
        {"provider_user_id": "google-123", "email": "oauth@example.com", "name": "OAuth User"}
    )

    response = client.post(
        "/api/v1/auth/oauth/login", json={"provider": "google", "id_token": "fake-token"}
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["user"]["email"] == "oauth@example.com"
    assert body["access_token"]

    from app.models import OAuthAccount, User

    user = User.query.filter_by(email="oauth@example.com").first()
    assert user is not None
    assert user.password_hash is None

    account = OAuthAccount.query.filter_by(provider="google", provider_user_id="google-123").first()
    assert account is not None
    assert account.user_id == user.id


def test_oauth_login_reuses_existing_link(client, fake_google_verifier):
    fake_google_verifier(
        {"provider_user_id": "google-123", "email": "oauth@example.com", "name": "OAuth User"}
    )

    first = client.post(
        "/api/v1/auth/oauth/login", json={"provider": "google", "id_token": "fake-token"}
    )
    second = client.post(
        "/api/v1/auth/oauth/login", json={"provider": "google", "id_token": "fake-token"}
    )

    assert first.status_code == 201
    assert second.status_code == 200  # already linked, not created again
    assert first.get_json()["user"]["id"] == second.get_json()["user"]["id"]


def test_oauth_login_links_existing_email_instead_of_duplicating(client, fake_google_verifier):
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "password": "s3cret!",
            "state": "California",
            "city": "Oakland",
        },
    )
    fake_google_verifier(
        {"provider_user_id": "google-999", "email": "ada@example.com", "name": "Ada"}
    )

    response = client.post(
        "/api/v1/auth/oauth/login", json={"provider": "google", "id_token": "fake-token"}
    )
    assert response.status_code == 200  # linked to the existing user, not a new one
    assert response.get_json()["user"]["email"] == "ada@example.com"


def test_oauth_login_rejects_unsupported_provider(client):
    response = client.post(
        "/api/v1/auth/oauth/login", json={"provider": "facebook", "id_token": "x"}
    )
    assert response.status_code == 400


def test_oauth_login_rejects_invalid_token(client, monkeypatch):
    def _raise(_id_token):
        raise ValueError("bad token")

    monkeypatch.setitem(auth_ops.OAUTH_VERIFIERS, "google", _raise)
    response = client.post(
        "/api/v1/auth/oauth/login", json={"provider": "google", "id_token": "fake-token"}
    )
    assert response.status_code == 401
