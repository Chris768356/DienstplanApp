from DienstplanApp.extensions import db

# Hilfstabelle
shift_type_qualification = db.Table(
    "shift_type_qualification",
    db.Column("shift_type_id", db.Integer, db.ForeignKey("shift_type.id"), primary_key=True),
    db.Column("qualification_id", db.Integer, db.ForeignKey("qualification.id"), primary_key=True)
)

class Shift_Type(db.Model):
    __tablename__ = "shift_type"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=True)

    name = db.Column(db.String(254), nullable=False)
    start = db.Column(db.Time, nullable=False)
    end = db.Column(db.Time, nullable=False)

    qualifications = db.relationship("Qualification", secondary=shift_type_qualification)
