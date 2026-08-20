from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.security import generate_password_hash

from DienstplanApp.extensions import db
from DienstplanApp.models.role import Role
from DienstplanApp.models.user import User
from DienstplanApp.models.user_login import User_login
from DienstplanApp.services.validate import (
    check_email,
    validate_email,
    validate_password,
)

auth = Blueprint("auth",__name__)

@auth.after_request
def add_header(response):
    """Verhindert, dass der Browser Seiten dieses Blueprints im Cache speichert."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@auth.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        firstname = request.form.get("firstname", "").strip()
        lastname = request.form.get("lastname", "").strip()
        email = request.form.get("email", "").strip()
        email_confirm = request.form.get("email-confirm", "").strip()
        password = request.form.get("password", "")
        agb = request.form.get("agb", "")
        dsgvo = request.form.get("dsgvo", "")
        password_confirm = request.form.get("password-confirm", "")
        #invite_code = request.form.get("invite-code", "").strip()

        form_data = request.form.to_dict()
        ignore_fields = ['password', 'password-confirm']
        for field in ignore_fields:
            form_data.pop(field, None)

        form_data = ImmutableMultiDict(form_data)
        
        if len(firstname) < 1 or len (firstname) > 155:
            flash("Vorname muss zwischen 1 und 155 Zeichen lang sein.", "error")
            return render_template("auth/register.html", form_data = form_data)

        elif len(lastname) < 1 or len (lastname) > 155:
            flash("Nachname muss zwischen 1 und 155 Zeichen lang sein.", "error")
            return render_template("auth/register.html", form_data = form_data)

        elif len(email) > 254:
            flash("Email darf nicht länger als 254 Zeichen sein.", "error")
            return render_template("auth/register.html", form_data = form_data)

        elif len(email_confirm) > 254:
                flash("Email Bestätigung darf nicht länger als 254 Zeichen sein.", "error")
                return render_template("auth/register.html", form_data = form_data)

        elif len(password) > 128:
            flash("Passwort darf nicht länger als 128 Zeichen sein.", "error")
            return render_template("auth/register.html", form_data = form_data)

        elif len(password_confirm) > 128:
            flash("Passwort Bestätigung darf nicht länger als 128 Zeichen sein.", "error")
            return render_template("auth/register.html", form_data = form_data)

        elif agb != "agb-accepted" or dsgvo != "dsgvo-accepted":
            flash("Bitte lesen und akzeptieren Sie die AGB und die DSGVO.", "error")
            return render_template("auth/register.html", form_data = form_data)

        elif not validate_email(email):
            flash("Bitte geben Sie eine gültige Email-Adresse ein.", "error")
            return render_template("auth/register.html", form_data = form_data)
        
        elif email != email_confirm:
            flash("Die E-Mail-Adressen stimmen nicht überein.", "error")
            return render_template("auth/register.html", form_data = form_data)

        elif not validate_password(password):
            flash("Das Passwort muss mindestens 12 Zeichen lang sein und mindestens einen Großbuchstaben, einen Kleinbuchstaben, eine Zahl und ein Sonderzeichen enthalten.", "error")
            return render_template("auth/register.html", form_data = form_data)
        
        elif password != password_confirm:
            flash("Die Passwörter stimmen nicht überein.", "error")
            return render_template("auth/register.html", form_data = form_data)

        else:
            if check_email(email):
                generate_password_hash(password)
            else:
                # Wir suchen die Standard-Rolle "Mitarbeiter" +++
                default_role = db.session.scalar(db.select(Role).where(Role.description == "Mitarbeiter"))

                # Datenbankeintrag wird erstellt
                user_login = User_login(email=email)
                user_login.set_password(password)
                db.session.add(user_login)
                db.session.commit()
                
                stmt = db.select(User_login).filter_by(email=email)
                user_login_id = db.session.execute(stmt).scalar()
                user_id = user_login_id.id
                
                # +++ übergeben die role_id an den User +++
                user = User(
                    login_id=user_id, 
                    firstname=firstname, 
                    lastname=lastname,
                    role_id=default_role.id if default_role else None
                )
                db.session.add(user)
                db.session.commit()

            flash(f"Willkommen {firstname} {lastname}! Registrierung erfolgreich.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form_data = {})


@auth.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password")

        stmt = db.select(User_login).filter_by(email=email)
        user = db.session.execute(stmt).scalar()

        if user:
            if user.check_password(password):
                login_user(user)
                return redirect(url_for("index"))
            else:
                flash("Email oder Passwort falsch.", "error")
        else:
            generate_password_hash(password)
            flash("Email oder Passwort falsch.", "error")

    return render_template("auth/login.html")


@auth.route("/logout")
@login_required
def logout():
    '''Benutzer ausloggen und auf Startseite weiterleiten'''
    logout_user()
    flash("Sie wurden erfolgreich ausgeloggt.", "success")
    return redirect(url_for("index"))
