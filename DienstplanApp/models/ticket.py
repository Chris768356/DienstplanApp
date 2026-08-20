from datetime import datetime

from DienstplanApp.extensions import db


class Ticket(db.Model):
    __tablename__ = "ticket"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.Text, nullable=False) # Text erlaubt längere Nachrichten
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Offen") # "Offen" oder "Erledigt"

    user = db.relationship("User")
