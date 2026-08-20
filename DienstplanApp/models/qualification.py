from DienstplanApp.extensions import db

class Qualification(db.Model):
    __tablename__ = "qualification"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(155), nullable = False)