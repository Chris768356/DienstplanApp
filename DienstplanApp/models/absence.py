from DienstplanApp.extensions import db


class Absence(db.Model):
    __tablename__ = "absence"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(155), nullable=False)
    status = db.Column(db.Boolean, default=True, nullable=False)
    
    user = db.relationship("User")
