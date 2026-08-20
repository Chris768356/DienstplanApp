from DienstplanApp.extensions import db

class Company(db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key = True)
    company_name = db.Column(db.String(255), unique = True, nullable = False)
    street = db.Column(db.String(255))
    house_number = db.Column(db.String(10))
    zip_code = db.Column(db.String(10))
    city = db.Column(db.String(255))
    phone_number  = db.Column(db.String(50))
    email = db.Column(db.String(255), unique = True)
