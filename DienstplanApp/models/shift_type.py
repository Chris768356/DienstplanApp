from DienstplanApp.extensions import db

class Shift_Type(db.Model):
    __tablename__ = "shift_type"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(254))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)



    