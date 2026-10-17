"""Which account each email is sent from (app/email.py)."""
import pytest

from app.email import MAIL_ACCOUNT_DEFAULT, MAIL_ACCOUNT_NOREPLY, make_mail_account, send_email
from app.extensions import mail


def sent_from(account):
    with mail.record_messages() as outbox:
        send_email("Hi", ["someone@example.com"], "body", "<p>body</p>", account=account)
    [message] = outbox
    return message.sender


def test_default_account_sends_from_mail_username(app):
    assert sent_from(MAIL_ACCOUNT_DEFAULT) == app.config["MAIL_USERNAME"]
    assert make_mail_account(app, MAIL_ACCOUNT_DEFAULT).username == app.config["MAIL_USERNAME"]


def test_noreply_account_sends_and_authenticates_as_noreply(app):
    assert sent_from(MAIL_ACCOUNT_NOREPLY) == "noreply@example.com"
    account = make_mail_account(app, MAIL_ACCOUNT_NOREPLY)
    assert (account.username, account.password) == ("noreply@example.com", "noreply-password")


def test_noreply_without_password_is_an_alias_of_the_default_account(app):
    app.config["NOREPLY_MAIL_PASSWORD"] = None
    assert sent_from(MAIL_ACCOUNT_NOREPLY) == "noreply@example.com"
    assert make_mail_account(app, MAIL_ACCOUNT_NOREPLY).username == app.config["MAIL_USERNAME"]


@pytest.mark.parametrize("username", [None, ""])
def test_unconfigured_noreply_falls_back_to_the_default_account(app, username):
    app.config["NOREPLY_MAIL_USERNAME"] = username
    assert sent_from(MAIL_ACCOUNT_NOREPLY) == app.config["MAIL_USERNAME"]


def test_message_notifications_come_from_noreply(app, client):
    def register(email, name):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "name": name,
                "email": email,
                "password": "s3cret!",
                "state": "Madrid",
                "city": "Madrid",
                "registration_key": "test-registration-key",
            },
        )
        return response.get_json()

    alice = register("alice@example.com", "Alice")
    bob = register("bob@example.com", "Bob")
    with mail.record_messages() as outbox:
        response = client.post(
            f"/api/v1/users/{bob['user']['id']}/messages",
            json={"subject": "Hi", "body": "Still available?"},
            headers={"Authorization": f"Bearer {alice['access_token']}"},
        )
    assert response.status_code == 201, response.get_json()
    [notification] = outbox
    assert notification.recipients == ["bob@example.com"]
    assert notification.subject == "[Marketplace] from Alice: Hi"
    assert notification.sender == "noreply@example.com"
