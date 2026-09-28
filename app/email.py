from threading import Thread

from flask import current_app
from flask_mail import Message

from app.extensions import mail
from app.utils.logger import logger


def _send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            logger.error(f"Failed to send email '{msg.subject}' to {msg.recipients}")
            logger.catch_exception(e)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=_send_async_email, args=(current_app._get_current_object(), msg)).start()
