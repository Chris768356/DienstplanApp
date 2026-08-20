from DienstplanApp.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User_login(db.Model):
    __tablename___ = "user_login"

    id = db.Column(db.Integer, primary_key = True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    email = db.Column(db.String(254), unique = True , nullable = False)
    password_hash = db.Column(db.String(255), nullable = False)

    def set_password(self, password):
        """Hasht das Passwort und speichert es in der DB"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ Prüft, ob das eingegeben Passwort zum Hash passt"""
        return check_password_hash(self.password_hash, password)