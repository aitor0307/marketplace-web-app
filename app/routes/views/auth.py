from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.forms import LoginForm, RegistrationForm
from app.routes.operations.auth_ops import authenticate_user, register_user

views_auth_bp = Blueprint("views_auth", __name__)


@views_auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views_listings.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = authenticate_user(form.email.data, form.password.data)
        if user is None:
            flash("Invalid username or password")
            return redirect(url_for("views_auth.login"))
        login_user(user)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("views_listings.index")
        return redirect(next_page)
    return render_template("login.html", title="Login", form=form)


@views_auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out")
    return redirect(url_for("views_listings.index"))


@views_auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("views_listings.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        register_user(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,
            state=form.state.data,
            city=form.city.data,
        )
        flash("You've been registered")
        return redirect(url_for("views_auth.login"))
    return render_template("register.html", title="Register", form=form)
