"""Outgoing email, sent from one of several configured accounts.

MAIL_ACCOUNT_DEFAULT is the main Gmail account (MAIL_USERNAME/MAIL_PASSWORD);
it only sends mail meant for us, like registration approval requests.
MAIL_ACCOUNT_NOREPLY (NOREPLY_MAIL_USERNAME/NOREPLY_MAIL_PASSWORD) sends
everything users receive. Both share MAIL_SERVER/PORT/TLS.

The noreply account degrades gracefully:
  - no NOREPLY_MAIL_USERNAME: sends exactly like the default account;
  - a username but no password: authenticates as the default account and only
    sets From to the noreply address (Gmail needs it as a "Send mail as" alias
    of the default account, or it rewrites From);
  - both: authenticates as the noreply account itself.
"""
from threading import Thread

from flask import current_app
from flask_mail import Connection, Message

from app.extensions import mail
from app.utils.logger import logger

MAIL_ACCOUNT_DEFAULT = "default"
MAIL_ACCOUNT_NOREPLY = "noreply"


def mail_account_settings(config, account):
    """Flask-Mail settings (MAIL_* keys) for ``account``, from app config."""
    settings = {key: value for key, value in config.items() if key.startswith("MAIL_")}
    settings["MAIL_DEFAULT_SENDER"] = config.get("MAIL_DEFAULT_SENDER") or config.get("MAIL_USERNAME")

    noreply_username = config.get("NOREPLY_MAIL_USERNAME")
    if account == MAIL_ACCOUNT_NOREPLY and noreply_username:
        settings["MAIL_DEFAULT_SENDER"] = noreply_username
        if config.get("NOREPLY_MAIL_PASSWORD"):
            settings["MAIL_USERNAME"] = noreply_username
            settings["MAIL_PASSWORD"] = config["NOREPLY_MAIL_PASSWORD"]
    return settings


def make_mail_account(app, account):
    """Factory: a Flask-Mail state for ``account``, usable with Connection()."""
    return mail.init_mail(mail_account_settings(app.config, account), app.debug, app.testing)


def _deliver(app, account, msg):
    with app.app_context():
        try:
            with Connection(make_mail_account(app, account)) as connection:
                msg.send(connection)
        except Exception as e:
            logger.error(f"Failed to send email '{msg.subject}' to {msg.recipients} via {account}")
            logger.catch_exception(e)


def send_email(
    subject, recipients, text_body, html_body, account=MAIL_ACCOUNT_NOREPLY, reply_to=None
):
    """Send from ``account`` (noreply unless told otherwise); the From address
    is that account's. Delivery happens on a background thread unless
    MAIL_SEND_ASYNC is off (tests)."""
    app = current_app._get_current_object()
    msg = Message(
        subject,
        sender=mail_account_settings(app.config, account)["MAIL_DEFAULT_SENDER"],
        recipients=recipients,
        reply_to=reply_to,
    )
    msg.body = text_body
    msg.html = html_body
    if app.config.get("MAIL_SEND_ASYNC", True):
        Thread(target=_deliver, args=(app, account, msg)).start()
    else:
        _deliver(app, account, msg)
