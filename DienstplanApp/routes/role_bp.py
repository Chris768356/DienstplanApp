from datetime import datetime, timedelta, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from DienstplanApp.decorators import (
    admin_required,
    company_required,
    planer_or_admin_required,
)
from DienstplanApp.extensions import db
from DienstplanApp.models.company import Company
from DienstplanApp.models.department import Department
from DienstplanApp.models.invite_code import InviteCode
from DienstplanApp.models.role import Role
from DienstplanApp.models.user import User

role_bp = Blueprint("role", __name__)

@role_bp.route("/setup")
@login_required
def setup_roles():
    """Einmalige Route, um die Standard-Rollen zu erstellen und dir den Admin zu geben."""
    
    # Rollen anlegen
    standard_rollen = ["Admin", "Planer", "Mitarbeiter"]
    
    for rollen_name in standard_rollen:
        # Rollenprüfung
        existing_role = db.session.scalar(db.select(Role).where(Role.description == rollen_name))
        if not existing_role:
            new_role = Role(description=rollen_name)
            db.session.add(new_role)
            
    db.session.commit()

    # Admin setzen
    admin_role = db.session.scalar(db.select(Role).where(Role.description == "Admin"))
    
    # Zuweisung Admin-Rolle
    current_user.user_data.role_id = admin_role.id
    db.session.commit()

    flash("Zauberei erfolgreich: Die Rollen wurden angelegt und du bist jetzt Admin!", "success")
    return redirect(url_for("profile.profile"))

@role_bp.route("/manage", methods=["GET", "POST"])
@login_required
@admin_required
def manage_roles():
    """Zeigt alle Nutzer an und lässt den Admin die Rollen ändern."""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        new_role_id = request.form.get("role_id")

        # +++ Der Selbst-Aussperr-Schutz +++
        # current_user.user_data.id ist deine eigene ID
        if int(user_id) == current_user.user_data.id:
            flash("Sicherheitswarnung: Du kannst deine eigenen Admin-Rechte nicht ändern!", "error")
            return redirect(url_for("role.manage_roles"))

        # Den ausgewählten Nutzer aus der Datenbank laden
        target_user = db.session.get(User, int(user_id))
        if target_user:
            target_user.role_id = int(new_role_id)
            db.session.commit()
            flash(f"Rechte für {target_user.firstname} {target_user.lastname} wurden aktualisiert!", "success")
        
        return redirect(url_for("role.manage_roles"))

    # Für die Ansicht laden wir alle User und alle verfügbaren Rollen
    users = db.session.scalars(db.select(User).order_by(User.lastname)).all()
    roles = db.session.scalars(db.select(Role)).all()

    return render_template("role/manage_roles.html", users=users, roles=roles)


@role_bp.route("/invite", methods=["GET", "POST"])
@login_required
@company_required
@planer_or_admin_required
def generate_invite():
    """Seite zum Erstellen und Verwalten von Einladungscodes."""
    user_data = getattr(current_user, 'user_data', None)
    role = user_data.role.description if user_data and user_data.role else None
    my_company_id = user_data.company_id if user_data else None

    if request.method == "POST":
        # Admin kann Firma wählen, Planer übergibt immer seine eigene
        company_id = request.form.get("company_id")
        department_id = request.form.get("department_id")
        valid_days = int(request.form.get("valid_days", 7)) # Standard: 7 Tage

        if not company_id:
            company_id = my_company_id

        # Ablaufdatum berechnen
        expires_at = datetime.now(timezone.utc) + timedelta(days=valid_days)

        new_code = InviteCode(
            code=InviteCode.generate_random_code(),
            company_id=int(company_id),
            department_id=int(department_id) if department_id else None,
            expires_at=expires_at
        )
        db.session.add(new_code)
        db.session.commit()

        flash(f"Einladungscode '{new_code.code}' erfolgreich erstellt!", "success")
        return redirect(url_for("role.generate_invite"))

    # Für die Dropdowns laden wir die passenden Daten
    if role == 'Admin':
        companies = db.session.scalars(db.select(Company)).all()
        departments = db.session.scalars(db.select(Department)).all()
        # Admin sieht alle aktiven Codes
        active_codes = db.session.scalars(db.select(InviteCode).where(InviteCode.expires_at > datetime.now(timezone.utc))).all()
    else:
        companies = db.session.scalars(db.select(Company).where(Company.id == my_company_id)).all()
        departments = db.session.scalars(db.select(Department).where(Department.company_id == my_company_id)).all()
        # Planer sieht nur Codes seiner Firma
        active_codes = db.session.scalars(db.select(InviteCode).where(InviteCode.company_id == my_company_id, InviteCode.expires_at > datetime.now(timezone.utc))).all()

    return render_template("role/generate_invite.html", companies=companies, departments=departments, active_codes=active_codes)
