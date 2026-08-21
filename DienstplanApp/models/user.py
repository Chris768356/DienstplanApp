from DienstplanApp.extensions import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key = True)
    login_id = db.Column(db.Integer, db.ForeignKey('user_login.id'), nullable = False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    firstname =  db.Column(db.String(155), nullable = False)
    lastname = db.Column(db.String(155), nullable = False)
    weekly_hours = db.Column(db.Numeric(precision = 5, scale = 2))
    is_active = db.Column(db.Boolean, default = True, nullable = False) 