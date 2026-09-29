from flask import Blueprint, current_app, g, jsonify, request, url_for
from markupsafe import escape
from sqlalchemy import and_, or_

from app.decorators.auth import jwt_verify
from app.decorators.docs import api_doc
from app.email import send_email
from app.models import Listing, Message, User
from app.schemas.messages import SendMessagePayload
from app.utils.logger import logger

messages_ops_bp = Blueprint("ops_messages", __name__, url_prefix="/api/v1/users")


def get_conversation(user, other_user):
    return (
        Message.query.filter(
            or_(
                and_(Message.sender_id == user.id, Message.recipient_id == other_user.id),
                and_(Message.sender_id == other_user.id, Message.recipient_id == user.id),
            )
        )
        .order_by(Message.timestamp.desc())
        .all()
    )


def get_user_messages(user):
    return (
        Message.query.filter(or_(Message.sender_id == user.id, Message.recipient_id == user.id))
        .order_by(Message.timestamp.desc())
        .all()
    )


def serialize_message(message):
    data = message.to_dict()
    data["sender"] = message.sender.to_summary() if message.sender else None
    data["recipient"] = message.recipient.to_summary() if message.recipient else None
    data["listing"] = (
        {"id": message.listing.id, "title": message.listing.title} if message.listing else None
    )
    return data


def profile_url_for(user):
    # The React app owns user pages; the Jinja view is only the fallback
    # until FRONTEND_URL is configured everywhere.
    frontend_url = current_app.config.get("FRONTEND_URL")
    if frontend_url:
        return "{}/users/{}".format(frontend_url.rstrip("/"), user.id)
    return current_app.config["HOST"] + url_for("views_users.view_user", user_id=user.id)


def send_message(sender, recipient, subject, body, listing_id=None):
    if listing_id is not None:
        listing = Listing.get_by_id(listing_id)
        if listing is None:
            return None, "Listing not found"
        if listing.user_id != recipient.id:
            return None, "Listing does not belong to the recipient"

    message = Message.create(
        sender_id=sender.id,
        recipient_id=recipient.id,
        listing_id=listing_id,
        subject=subject,
        body=body,
    )

    try:
        profile_url = profile_url_for(sender)
        html = (
            "<p>You've received a new message from "
            "<a href='{profile_url}'>{name}</a> on Marketplace.</p>"
            "<p>Subject: {subject}</p><p>Message: {body}</p>"
        ).format(
            profile_url=escape(profile_url),
            name=escape(sender.name),
            subject=escape(subject),
            body=escape(body),
        )
        send_email(
            "Message from {} on Marketplace".format(sender.name),
            current_app.config["MAIL_USERNAME"],
            [recipient.email],
            html,
            html,
        )
    except Exception as e:
        # The message is already stored, so a mail failure must not fail the request.
        logger.error(f"Failed to send email for message {message.id} to user {recipient.id}")
        logger.catch_exception(e)

    return message, None


@messages_ops_bp.route("/<int:user_id>/messages", methods=["POST"])
@api_doc("Send another user a message", tags=["messages"], request_model=SendMessagePayload)
@jwt_verify()
def send_message_operation(user_id):
    sender = User.get_by_id(g.user_id)
    recipient = User.get_by_id(user_id)
    if recipient is None:
        return jsonify(error="User not found"), 404

    payload = SendMessagePayload(**(request.get_json(silent=True) or {}))
    message, error = send_message(
        sender, recipient, payload.subject, payload.body, listing_id=payload.listing_id
    )
    if error:
        return jsonify(error=error), 400
    return jsonify(sent=True, message=serialize_message(message)), 201


@messages_ops_bp.route("/<int:user_id>/messages", methods=["GET"])
@api_doc(
    "List messages, newest first",
    description="On your own id: every message you sent or received. On another "
    "user's id: only your conversation with them.",
    tags=["messages"],
)
@jwt_verify()
def list_messages_operation(user_id):
    current = User.get_by_id(g.user_id)
    other = User.get_by_id(user_id)
    if other is None:
        return jsonify(error="User not found"), 404

    messages = get_user_messages(current) if other.id == current.id else get_conversation(current, other)
    return jsonify(messages=[serialize_message(message) for message in messages])
