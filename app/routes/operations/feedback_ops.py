from flask import Blueprint, current_app, g, jsonify, request
from markupsafe import escape

from app.decorators.auth import jwt_verify
from app.decorators.docs import api_doc
from app.email import MAIL_ACCOUNT_DEFAULT, send_email
from app.models import User
from app.schemas.feedback import FeedbackKind, SendFeedbackPayload
from app.utils.logger import logger

feedback_ops_bp = Blueprint("ops_feedback", __name__, url_prefix="/api/v1/feedback")

FEEDBACK_SUBJECTS = {
    FeedbackKind.BUG: "Marketplace bug report from {}",
    FeedbackKind.IMPROVEMENT: "Marketplace improvement idea from {}",
}


def send_feedback(user, kind, message, page=None):
    """Email the feedback to FEEDBACK_EMAIL; replying goes straight to the user."""
    html = (
        "<p><strong>{kind}</strong> from {name} &lt;{email}&gt;</p>"
        "<p>Page: {page}</p>"
        "<p style='white-space: pre-wrap'>{message}</p>"
    ).format(
        kind="Bug report" if kind == FeedbackKind.BUG else "Improvement idea",
        name=escape(user.name),
        email=escape(user.email),
        page=escape(page or "-"),
        message=escape(message),
    )
    # Mail for us comes from the default account (see app/email.py).
    send_email(
        FEEDBACK_SUBJECTS[kind].format(user.name),
        [current_app.config["FEEDBACK_EMAIL"]],
        html,
        html,
        account=MAIL_ACCOUNT_DEFAULT,
        reply_to=user.email,
    )


@feedback_ops_bp.route("", methods=["POST"])
@api_doc(
    "Report a bug or suggest an improvement; it is emailed to FEEDBACK_EMAIL",
    tags=["feedback"],
    request_model=SendFeedbackPayload,
)
@jwt_verify()
def send_feedback_operation():
    payload = SendFeedbackPayload(**(request.get_json(silent=True) or {}))
    if not current_app.config.get("FEEDBACK_EMAIL"):
        return jsonify(error="Feedback isn't configured on this server"), 503
    user = User.get_by_id(g.user_id)
    try:
        send_feedback(user, payload.kind, payload.message.strip(), payload.page)
    except Exception as e:
        logger.error(f"Failed to send feedback from user {user.id}")
        logger.catch_exception(e)
        return jsonify(error="Unable to send your feedback right now"), 502
    return jsonify(sent=True), 202
