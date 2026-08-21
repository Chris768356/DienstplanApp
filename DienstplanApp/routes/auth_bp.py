from flask import Blueprint, request , render_template, flash, redirect, url_for
from werkzeug.datastructures import ImmutableMultiDict
from DienstplanApp.extensions import db
from DienstplanApp.models.user_login import User_login
from werkzeug.security import generate_password_hash
from DienstplanApp.models.user import User
from flask_login import login_user, login_required, logout_user, current_user
from DienstplanApp.services.validate import validate_password, validate_email, check_email
import re

auth = Blueprint("auth",__name__)

# EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
# PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$"

# def validate_password(password :str) -> bool:
#     '''Vergleicht ein eingegebenes Passwort mit dem regulären Ausdruck'''
#     if re.match(PASSWORD_REGEX, password):
#         return True
#     return False

# def validate_email(email :str) -> bool:
#     '''Vergleicht ein eingegebene Email Adresse mit dem regulären Ausdruck'''
#     if re.match(EMAIL_REGEX, email):
#         return True
#     return False

# def check_email(email :str) -> bool:
#     '''Prüft ob die im Formular eingegebene E-Mail Adresse schon vergeben ist'''
#     stmt = db.select(User_login).filter_by(email = email)
#     check = db.session.execute(stmt).first() is not None
#     return check

@auth.route("/register", methods =["GET","POST"])
def register():

    if request.method == "POST":
        firstname = request.form.get("firstname", "").strip()
        lastname = request.form.get("lastname","").strip()
        email = request.form.get("email", "").strip()
        email_confirm = request.form.get("confirm-email","").strip()
        password = request.form.get("password","")
        password_confirm = request.form.get("confirm-password","")
        agb = request.form.get("agb", "")
        dsgvo = request.form.get("dsgvo", "")
        invite_code = request.form.get("invite-code", "").strip() 

        form_data = request.form.to_dict()

        ignore_fields = ['password', 'password-confirm']

        for field in ignore_fields:
            form_data.pop(field, None)

        form_data = ImmutableMultiDict(form_data)

        if len(firstname) < 1 or len(firstname) > 155:
            flash("Vorname muss mehr als 1 und weniger als 155 Zeichen haben.", "error")
            return render_template("auth/register.html", form_data = form_data)

        elif len(lastname) < 1 or len(lastname) > 155:
            flash("Nachname muss mehr als 1 und weniger als 155 Zeichen haben", "errro")
            return render_template("auth/register.html", form_data = form_data)

        elif len(email) > 254:
            flash("Die E-Mail Adresse ist zu lang", "error")
            return render_template("auth/register.html", form_data = form_data)
        elif len(email_confirm) > 254:
            flash("Die E-Mail Adresse ist zu lang", "error")
            return render_template("auth/register.html", form_data = form_data)

        elif len(password) > 128:
            flash("Das Passwort darf nicht länger als 128 Zeichen sein", "error")
            return render_template("auth/register.html", form_data = form_data)
        elif len(password_confirm) > 128 :
            flash("Das Passwort darf nicht länger als 128 Zeichen sein", "error")
            return render_template("auth/register.html", form_data = form_data)

        elif agb  != "agb-accepted" and dsgvo != "dsgvo-accepted": 
            flash("Bitte die AGB und DSGVO lesen und akzeptieren", "error")
            return render_template("auth/register.html", form_data = form_data)

        elif not validate_email(email):
            flash("Bitte geben Sie eine gültige E-Mail Adresse an im Format beispiel@domain.de", "error")
            return render_template("auth/register.html", form_data = form_data)
        elif email != email_confirm:
            flash("Ihre E-Mail Adressen stimmen nicht überrein", "error")
            return render_template("auth/register.html", form_data = form_data)

        elif not validate_password(password):
            flash("Das Passwort muss mindestens 12 Zeichen lang, einen Großbuchtsaben, einen Kleinbuchstaben, eine Zahl und ein Sonderzeichen enthalten", "error")
            return render_template("auth/register.html", form_data = form_data)
        elif password != password_confirm:
            flash("Die eingegebenen Passwörter stimmen nicht überein", "error")
            return render_template("auth/register.html", form_data = form_data)

        else: 
            if check_email(email):
                generate_password_hash(password)
            else: 
                user_login = User_login(email = email)
                user_login.set_password(password)
                db.session.add(user_login)
                db.session.commit()
                stmt = db.select(User_login).filter_by(email = email)
                user_login_id = db.session.execute(stmt).scalar()
                user_id = user_login_id.id
                user = User(login_id = user_id, firstname = firstname, lastname = lastname)
                db.session.add(user)
                db.session.commit()
            flash(f"Wilkommen {firstname} {lastname}! Danke für ihre Registrierung.","succes")
            return redirect(url_for("auth.login"))
            
    return render_template("auth/register.html", form_data = {})

@auth.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").strip()
        password = request.form.get("password")

        stmt = db.select(User_login).filter_by(email = email)
        user = db.session.execute(stmt).scalar()

        if user:
            if user.check_password(password):
                login_user(user)
                return redirect(url_for("index"))
            else: 
                flash("Email oder Passwort falsch!", "error")
        else:
            generate_password_hash(password)
            flash("Email oder Passwort falsch!","error")
        
    return render_template("auth/login.html")

@auth.route("/logout")
def logout():
    '''Loggt einen Benutzer aus'''
    logout_user()
    flash("Sie haben sich erfolgreich abgemeldet")
    return redirect(url_for("index"))

