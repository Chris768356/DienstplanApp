from DienstplanApp.extensions import db


class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(55))
