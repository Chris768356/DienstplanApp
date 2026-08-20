import re

from DienstplanApp.extensions import db
from DienstplanApp.models.user_login import User_login

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$"

def validate_password(password :str) -> bool:
    '''Vergleicht ein eingegebenes Passwort mit dem Regex und gibt True zurück, wenn es den Anforderungen entspricht, ansonsten False'''
    if re.match(PASSWORD_REGEX, password):
        return True
    return False

def validate_email(email :str) -> bool:
    '''Vergleicht eine eingegebene Email mit dem Regex und gibt True zurück, wenn sie den Anforderungen entspricht, ansonsten False'''
    if re.match(EMAIL_REGEX, email):
        return True
    return False

def check_email(email :str) -> bool:
    '''Prüft Email ob bereits im Formular vergeben ist'''
    stmt = db.select(User_login).filter_by(email=email)
    check = db.session.execute(stmt).first() is not None
    return check