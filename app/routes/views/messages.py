from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.forms import MessageForm
from app.routes.operations.messages_ops import send_message
from app.routes.operations.users_ops import get_user

views_messages_bp = Blueprint("views_messages", __name__)


@views_messages_bp.route("/message/<int:user_id>", methods=["GET", "POST"])
@login_required
def message(user_id):
    recipient = get_user(user_id)
    if recipient is None:
        abort(404)
    form = MessageForm()
    if form.validate_on_submit():
        send_message(current_user, recipient, form.subject.data, form.body.data)
        flash("Message sent")
        return redirect(url_for("views_users.view_user", user_id=user_id))
    return render_template("message.html", title="Send Message", form=form, user=recipient, current_user=current_user)
