import re
PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$"
def validate_password(password :str) -> bool:
    '''Vergleicht ein eingegebenes Passwort mit dem regulärem Ausdruck'''
    if re.match(PASSWORD_REGEX, password):
        return True
    return False
print(validate_password("asdf1234ASDF_"))
print(validate_password("asdf1234ASDF"))
