from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from DienstplanApp.extensions import db

# 1. Die Hilfstabelle (m:n)
user_qualification = db.Table(
    "user_qualification",
    db.Column("user_id", ForeignKey("user.id"), primary_key=True), 
    db.Column("qualification_id", ForeignKey("qualification.id"), primary_key=True),
)

# 2. Das Qualifikations-Modell in SQLAlchemy 2.0 Syntax
class Qualification(db.Model):
    __tablename__ = "qualification"
    
    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("company.id"))

    name: Mapped[str] = mapped_column(String(155), nullable=False)
    
    # Hier verwenden wir nun das kleingeschriebene 'list'
    users: Mapped[list["User"]] = relationship(
        secondary=user_qualification, 
        back_populates="qualifications"
    )
