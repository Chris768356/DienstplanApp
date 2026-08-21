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
    
    # Gültigkeit & Metadaten
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Wer und Wann (modernes UTC ohne Deprecation-Warnung)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    # Beziehungen
    company = db.relationship("Company")
    department = db.relationship("Department")
    creator = db.relationship("User", foreign_keys=[creator_id])

    @staticmethod
    def generate_random_code():
        """Generiert einen zufälligen, 8-stelligen Code (z.B. a3f9b2c1)"""
        return secrets.token_hex(4)
