from flask import Blueprint, current_app, g, jsonify, url_for

from app.decorators.auth import jwt_verify
from app.decorators.docs import api_doc
from app.decorators.validation import validate_payload
from app.email import send_email
from app.models import User
from app.schemas.messages import SendMessagePayload

messages_ops_bp = Blueprint("ops_messages", __name__, url_prefix="/api/v1/users")


def send_message(sender, recipient, subject, body):
    profile_url = current_app.config["HOST"] + url_for("views_users.view_user", user_id=sender.id)
    html = (
        "<p>You've received a new message from "
        "<a href='{profile_url}'>{name}</a> on Marketplace.</p>"
        "<p>Subject: {subject}</p><p>Message: {body}</p>"
    ).format(profile_url=profile_url, name=sender.name, subject=subject, body=body)
    send_email(
        "Message from {} on Marketplace".format(sender.name),
        current_app.config["MAIL_USERNAME"],
        [recipient.email],
        html,
        html,
    )


@messages_ops_bp.route("/<int:user_id>/messages", methods=["POST"])
@api_doc("Send another user a message", tags=["messages"])
@jwt_verify()
@validate_payload(SendMessagePayload)
def send_message_operation(user_id, payload: SendMessagePayload):
    sender = User.get_by_id(g.user_id)
    recipient = User.get_by_id(user_id)
    if recipient is None:
        return jsonify(error="User not found"), 404
    send_message(sender, recipient, payload.subject, payload.body)
    return jsonify(sent=True), 201
