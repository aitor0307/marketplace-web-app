import io

import pytest

from app.routes.operations import auth_ops


@pytest.fixture
def approval_emails(monkeypatch):
    sent = []
    monkeypatch.setattr(
        "app.routes.operations.auth_ops.send_email",
        lambda subject, recipients, text_body, html_body, account: sent.append(
            {"subject": subject, "recipients": recipients, "html": html_body, "account": account}
        ),
    )
    return sent


def register(client, **overrides):
    payload = {
        "name": "Ada",
        "email": "ada@example.com",
        "password": "s3cret!",
        "state": "Madrid",
        "city": "Madrid",
    }
    payload.update(overrides)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()


def emails_to(sent, recipient):
    return [email for email in sent if email["recipients"] == [recipient]]


def approval_token(email):
    return email["html"].split("/approvals/", 1)[1].split("'", 1)[0]


def post_listing(client, access_token):
    return client.post(
        "/api/v1/listings",
        data={
            "title": "Bike",
            "body": "Barely used",
            "condition": "Used",
            "price": "120",
            "images": [(io.BytesIO(b"fake-image-bytes"), "bike.png")],
        },
        headers={"Authorization": f"Bearer {access_token}"},
        content_type="multipart/form-data",
    )


@pytest.fixture(autouse=True)
def images_folder(app, tmp_path):
    app.config["IMAGES_FOLDER"] = str(tmp_path)


def test_registering_with_the_key_is_active_and_sends_no_email(client, approval_emails):
    auth = register(client, registration_key="test-registration-key")
    assert auth["user"]["status"] == "active"
    assert auth["contact_email"] is None
    assert approval_emails == []


@pytest.mark.parametrize("registration_key", [None, "", "wrong-key"])
def test_registering_without_the_key_is_pending_and_emails_approver_and_user(
    app, client, approval_emails, registration_key
):
    app.config["FRONTEND_URL"] = "https://app.example.com/"
    auth = register(client, registration_key=registration_key)
    assert auth["user"]["status"] == "pending"
    assert auth["contact_email"] == "support@example.com"

    assert len(approval_emails) == 2
    [to_approver] = emails_to(approval_emails, "approver@example.com")
    assert "ada@example.com" in to_approver["html"]
    assert "https://app.example.com/approvals/" in to_approver["html"]
    assert to_approver["account"] == "default"

    [to_user] = emails_to(approval_emails, "ada@example.com")
    assert "pending approval" in to_user["subject"]
    assert "support@example.com" in to_user["html"]
    assert to_user["account"] == "noreply"


def test_pending_users_cannot_publish_listings(client, approval_emails):
    auth = register(client)
    response = post_listing(client, auth["access_token"])
    assert response.status_code == 403
    assert response.get_json()["error"] == "Your account is pending approval"


def test_approval_link_activates_the_user_and_tells_them(app, client, approval_emails):
    app.config["FRONTEND_URL"] = "https://app.example.com/"
    auth = register(client)
    [to_approver] = emails_to(approval_emails, "approver@example.com")
    token = approval_token(to_approver)

    # Looking the link up is read-only.
    preview = client.get(f"/api/v1/auth/approvals/{token}")
    assert preview.status_code == 200
    assert preview.get_json()["user"]["status"] == "pending"

    assert len(emails_to(approval_emails, "ada@example.com")) == 1  # just the pending notice

    approved = client.post(f"/api/v1/auth/approvals/{token}")
    assert approved.status_code == 200
    assert approved.get_json()["user"]["status"] == "active"

    to_user = emails_to(approval_emails, "ada@example.com")
    assert len(to_user) == 2
    assert "approved" in to_user[-1]["subject"]
    assert to_user[-1]["account"] == "noreply"
    assert "https://app.example.com/login" in to_user[-1]["html"]

    # Approving again is a no-op (no second email), and the user can now publish.
    assert client.post(f"/api/v1/auth/approvals/{token}").status_code == 200
    assert len(emails_to(approval_emails, "ada@example.com")) == 2
    assert post_listing(client, auth["access_token"]).status_code == 201


def test_tampered_or_expired_approval_links_are_rejected(app, client, approval_emails):
    register(client)
    [to_approver] = emails_to(approval_emails, "approver@example.com")
    token = approval_token(to_approver)

    tampered = client.post(f"/api/v1/auth/approvals/{token}x")
    assert tampered.status_code == 400
    assert tampered.get_json()["error"] == "Invalid approval link"

    app.config["REGISTRATION_APPROVAL_MAX_AGE"] = -1
    expired = client.post(f"/api/v1/auth/approvals/{token}")
    assert expired.status_code == 400
    assert expired.get_json()["error"] == "This approval link has expired"


def test_new_oauth_users_are_pending(client, approval_emails, monkeypatch):
    monkeypatch.setitem(
        auth_ops.OAUTH_VERIFIERS,
        "google",
        lambda id_token: {"provider_user_id": "g-1", "email": "grace@example.com", "name": "Grace"},
    )
    response = client.post("/api/v1/auth/oauth/login", json={"provider": "google", "id_token": "x"})
    assert response.status_code == 201
    assert response.get_json()["user"]["status"] == "pending"
    assert len(emails_to(approval_emails, "approver@example.com")) == 1
    assert len(emails_to(approval_emails, "grace@example.com")) == 1
