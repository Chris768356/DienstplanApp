from DienstplanApp.extensions import db

class User_Qualification(db.Model):
    __tablename__ = "user_qualification"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    qualification_id = db.Column(db.Integer, db.ForeignKey("qualification.id"))