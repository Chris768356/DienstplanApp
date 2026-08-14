from DienstplanApp.extensions import db

class Shift(db.Model):
    __tablename__ = "shift"

    id = db.Column(db.Integer, primary_key = True)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"), nullable = False)
    shift_type_id = db.Column(db.Integer, db.ForeignKey("shift_type.id"), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    shift_date = db.Column(db.Date, nullable = False)
    shift_start = db.Column(db.DateTime)
    shift_end = db.Column(db.DateTime)

