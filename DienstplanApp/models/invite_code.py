import secrets
from datetime import datetime, timezone

from DienstplanApp.extensions import db


class InviteCode(db.Model):
    __tablename__ = "invite_code"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Zuweisungen
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"), nullable=True)
    
    # Gültigkeit
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # +++ Audit Trail +++
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    creator = db.relationship("User", foreign_keys=[created_by_id])

    company = db.relationship("Company")
    department = db.relationship("Department")

    @staticmethod
    def generate_random_code():
        """Generiert einen zufälligen, 8-stelligen Code (z.B. a3f9b2c1)"""
        return secrets.token_hex(4)
