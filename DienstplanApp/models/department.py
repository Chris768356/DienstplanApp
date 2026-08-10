from DienstplanApp.extensions import db

class Department(db.Model):
    __tablename__ = 'department'

    id = db.Column(db.Integer, primary_key = True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable = False)
    department_name = db.Column(db.String(155))
    
