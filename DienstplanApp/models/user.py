from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from DienstplanApp.extensions import db
from DienstplanApp.models.qualification import user_qualification

if TYPE_CHECKING:
    from DienstplanApp.models.qualification import Qualification

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Foreign Keys (nullable=False ist bei Mapped[int] automatisch der Standard)
    login_id: Mapped[int] = mapped_column(ForeignKey("user_login.id"))

    # Datenbank-Spalten (Foreign Keys)
    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("company.id"))
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("department.id"))
    
    # Beziehungen (Relationships) für dein Frontend
    company: Mapped[Optional["Company"]] = relationship()
    department: Mapped[Optional["Department"]] = relationship()
    
    # Strings mit fester Länge
    firstname: Mapped[str] = mapped_column(String(155))
    lastname: Mapped[str] = mapped_column(String(155))

    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    role = db.relationship("Role")
    
    # Numeric/Dezimalzahlen Typ 'Decimal'
    weekly_hours: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=2))
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Verbindung zu Qualifikationen +++
    qualifications: Mapped[list["Qualification"]] = relationship(
        secondary=user_qualification,
        back_populates="users"
    )