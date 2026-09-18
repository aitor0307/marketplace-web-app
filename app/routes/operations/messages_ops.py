from flask import Blueprint, current_app, jsonify, request, url_for
from flask_jwt_extended import get_jwt_identity

from app.decorators.auth import roles_required
from app.decorators.docs import api_doc
from app.email import send_email
from app.models import User

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
@roles_required()
def send_message_operation(user_id):
    sender = User.get_by_id(get_jwt_identity())
    recipient = User.get_by_id(user_id)
    if recipient is None:
        return jsonify(error="User not found"), 404
    data = request.get_json(silent=True) or {}
    if not data.get("subject") or not data.get("body"):
        return jsonify(error="subject and body are required"), 400
    send_message(sender, recipient, data["subject"], data["body"])
    return jsonify(sent=True), 201
