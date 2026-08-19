from flask import Blueprint, render_template, redirect, url_for, request,flash
from flask_login import login_required, current_user
from DienstplanApp.models.user_login import User_login
from DienstplanApp.models.user import User
from DienstplanApp.extensions import db
from DienstplanApp.services.validate import validate_email, validate_password, check_email

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/")
@login_required
def profile():
    return render_template("profile.html")

@profile_bp.route("/update_profile", methods = ["POST"])
@login_required
def update_profile():
    firstname = request.form.get("firstname").strip()
    lastname = request.form.get("lastname").strip()
    email = request.form.get("email").strip()
    email_confirm = request.form.get("email-confirm")

    if len(firstname) < 1 or len(firstname) > 155:
        flash("Vorname muss mehr als 1 und weniger als 155 Zeichen haben", "error")
        return redirect(url_for("profile.profile"))
    elif len(lastname) < 1 or len(lastname) > 155:
        flash("Nachname muss mehr als 1 und weniger als 155 Zeichen haben", "error")
        return redirect(url_for("profile.profile"))
    elif len(email) > 254:
        flash("E-Mail Adresse ist zu lang", "error")
        return redirect(url_for("profile.profile"))
    elif not validate_email(email):
        flash("Bitte geben sie eine gültige E-Mail Adresse im Format beispiel@domain.de an", "error")
        return redirect(url_for("profile.profile"))
    elif email != email_confirm:
        flash("Die E-Mail Adressen stimmen nicht überein","error")
        return redirect(url_for("profile.profile"))
    # else:
    #     if check_email(email): # Geht so nicht weil wenn email nicht geändert dann fehler

    return redirect(url_for("profile.profile"))