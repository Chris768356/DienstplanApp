from flask import Blueprint, request , render_template, flash
from werkzeug.datastructures import ImmutableMultiDict
from DienstplanApp.extensions import db
from DienstplanApp.models.user_login import User_login
import re

auth = Blueprint("auth",__name__)

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$"

def validate_password(password :str) -> bool:
    '''Vergleicht ein eingegebenes Passwort mit dem regulären Ausdruck'''
    if re.match(PASSWORD_REGEX, password):
        return True
    return False

def validate_email(email :str) -> bool:
    '''Vergleicht ein eingegebene Email Adresse mit dem regulären Ausdruck'''
    if re.match(EMAIL_REGEX, email):
        return True
    return False

def check_email(email :str) -> bool:
    '''Prüft ob die im Formular eingegebene E-Mail Adresse schon vergeben ist'''
    stmt = db.select(User_login).filter_by(email = email)
    check = db.session.execute(stmt).first() is not None
    return check

@auth.route("/register", methods =["GET","POST"])
def register():

    if request.method == "POST":
        firstname = request.form.get("firstname", "")
        lastname = request.form.get("lastname","")
        email = request.form.get("email", "")
        email_confirm = request.form.get("confirm_email","")
        password = request.form.get("password","")
        password_confirm = request.form.get("confirm_password","")
        invite_code = request.form.get("invite_code", "") 
    
    
    return render_template("auth/register.html")