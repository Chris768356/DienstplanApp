from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from DienstplanApp.decorators import company_required, planer_or_admin_required
from DienstplanApp.extensions import db
from DienstplanApp.models.company import Company
from DienstplanApp.models.department import Department
from DienstplanApp.models.invite_code import InviteCode
from DienstplanApp.models.qualification import Qualification
from DienstplanApp.models.user import User
from DienstplanApp.models.user_login import User_login
from DienstplanApp.services.validate import (
    check_email,
    validate_email,
    validate_password,
)

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/")
@login_required
def profile():
    companies = db.session.scalars(db.select(Company)).all()
    departments = db.session.scalars(db.select(Department)).all()
    qualifications = db.session.scalars(db.select(Qualification)).all()

    return render_template(
        "profile.html", 
        companies=companies, 
        departments=departments, 
        qualifications=qualifications
    )


@profile_bp.route("/update_profile", methods = ["POST"])
@login_required
def update_profile():
    firstname = request.form.get("firstname","").strip()
    lastname = request.form.get("lastname","").strip()
    email = request.form.get("email","").strip()
    email_confirm = request.form.get("email-confirm","").strip()

    company_id = request.form.get("company_id")
    department_id = request.form.get("department_id")

    selected_qual_ids = request.form.getlist("qualifications")

    if len(firstname) < 1 or len(firstname) > 155:
        flash("Vorname muss mehr als 1 und weniger als 155 Zeichen haben", "error")
        return redirect(url_for("profile.profile", mode="edit"))

    elif len(lastname) < 1 or len(lastname) > 155:
        flash("Nachname muss mehr als 1 und weniger als 155 Zeichen haben", "error")
        return redirect(url_for("profile.profile", mode="edit"))

    elif len(email) > 254:
        flash("E-Mail Adresse ist zu lang", "error")
        return redirect(url_for("profile.profile", mode="edit"))

    elif not validate_email(email):
        flash("Bitte geben Sie eine gültige E-Mail Adresse im Format beispiel@domain.de an!", "error")
        return redirect(url_for("profile.profile", mode="edit"))

    elif email != email_confirm:
        flash("Die Email Adressen stimmen nicht überein!", "error")
        return redirect(url_for("profile.profile", mode="edit"))

    if email != current_user.email:
        if check_email(email):        
            flash("Diese E-Mail Adresse wird bereits verwendet.", "error")
            return redirect(url_for("profile.profile", mode="edit"))
        
        # Wenn E-Mail neu und frei -> updaten
        current_user.email = email

    # Wir laden die echten Qualifikations-Objekte anhand dieser IDs aus der Datenbank
    if selected_qual_ids:
        selected_quals = db.session.scalars(
            db.select(Qualification).where(Qualification.id.in_(selected_qual_ids))
        ).all()
    else:
        selected_quals = [] # Wenn nichts angekreuzt wurde, ist die Liste leer

    # Vornamen und Nachnamen updaten
    current_user.user_data.firstname = firstname
    current_user.user_data.lastname = lastname

    current_user.user_data.company_id = int(company_id) if company_id else None
    current_user.user_data.department_id = int(department_id) if department_id else None

    current_user.user_data.qualifications = selected_quals

    # Änderungen in die Datenbank schreiben
    db.session.commit()
    flash("Dein Profil wurde erfolgreich aktualisiert!", "success")
    
    return redirect(url_for("profile.profile"))
