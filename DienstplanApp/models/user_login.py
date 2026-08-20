from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from DienstplanApp.extensions import db, login_manager


class User_login(db.Model, UserMixin):
    __tablename__ = "user_login"

    id = db.Column(db.Integer, primary_key = True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    email = db.Column(db.String(254), unique = True , nullable = False)
    password_hash = db.Column(db.String(255), nullable = False)
    user_data = db.relationship("User", backref="user_login", uselist=False)

    def set_password(self, password):
        """Hasht das Passwort und speichert es in der DB"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ Prüft, ob das eingegeben Passwort zum Hash passt"""
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    """Übergibt die ID aus dem Cookie und lädt den User aus der DB"""
    return db.session.get(User_login, int(user_id))
