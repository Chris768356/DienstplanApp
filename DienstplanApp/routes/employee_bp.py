from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from DienstplanApp.decorators import company_required, planer_or_admin_required
from DienstplanApp.extensions import db
from DienstplanApp.models.department import Department
from DienstplanApp.models.qualification import Qualification
from DienstplanApp.models.user import User

# url_prefix spart uns Tipparbeit: Alle Routen hier starten automatisch mit /employees
employee_bp = Blueprint("employee", __name__, url_prefix="/employees")

@employee_bp.route("/")
@login_required
@company_required
@planer_or_admin_required
def list_employees():
    """Zeigt eine filterbare Liste aller Mitarbeiter für Admin und Planer an."""
    user_data = current_user.user_data
    role = user_data.role.description if user_data and user_data.role else None
    my_company_id = user_data.company_id

    # Filter-Parameter aus der URL abgreifen
    department_id = request.args.get("department_id")
    qualification_id = request.args.get("qualification_id")

    # Basis-Abfrage aufbauen
    query = db.select(User)

    # Rechte prüfen: Planer sieht nur seine eigene Firma
    if role == "Planer":
        query = query.where(User.company_id == my_company_id)

    # Dynamische Filter anwenden
    if department_id:
        query = query.where(User.department_id == int(department_id))
    
    if qualification_id:
        # Prüft in der m:n Tabelle, ob der User diese Qualifikation besitzt
        query = query.where(User.qualifications.any(Qualification.id == int(qualification_id)))

    # Abfrage ausführen und alphabetisch sortieren
    users = db.session.scalars(query.order_by(User.lastname)).all()

    # Dropdown-Daten für die Filter laden
    if role == "Admin":
        departments = db.session.scalars(db.select(Department)).all()
    else:
        departments = db.session.scalars(db.select(Department).where(Department.company_id == my_company_id)).all()
        
    # Qualifikationen laden (fürs Erste laden wir alle verfügbaren)
    qualifications = db.session.scalars(db.select(Qualification)).all()

    return render_template(
        "employee/list_employees.html", 
        users=users, 
        departments=departments, 
        qualifications=qualifications,
        current_filters=request.args
    )

@employee_bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
@company_required
@planer_or_admin_required
def edit_employee(user_id):
    """Mitarbeiter-Details bearbeiten (Stammdaten, Stunden, Qualifikationen)."""
    user_data = current_user.user_data
    role = user_data.role.description if user_data and user_data.role else None
    my_company_id = user_data.company_id

    # Mitarbeiter aus der DB laden
    target_user = db.session.get(User, user_id)
    if not target_user:
        flash("Mitarbeiter nicht gefunden.", "error")
        return redirect(url_for("employee.list_employees"))

    # Sicherheits-Check für Planer: Geht es um einen User der eigenen Firma?
    if role == "Planer" and target_user.company_id != my_company_id:
        flash("Sicherheitswarnung: Keine Berechtigung für diesen Mitarbeiter.", "error")
        return redirect(url_for("employee.list_employees"))

    if request.method == "POST":
        # Stammdaten aktualisieren
        target_user.firstname = request.form.get("firstname", "").strip()
        target_user.lastname = request.form.get("lastname", "").strip()
        
        hours_str = request.form.get("weekly_hours")
        if hours_str:
            try:
                target_user.weekly_hours = float(hours_str)
            except ValueError:
                target_user.weekly_hours = None
        else:
            target_user.weekly_hours = None

        # Checkbox für Aktiv/Inaktiv (wenn nicht gesetzt, ist es False)
        target_user.is_active = True if request.form.get("is_active") == "on" else False

        # Qualifikationen aktualisieren (m:n Beziehung neu setzen)
        selected_qual_ids = request.form.getlist("qualifications")
        target_user.qualifications.clear()  # Alte Verknüpfungen löschen
        
        for q_id in selected_qual_ids:
            qual = db.session.get(Qualification, int(q_id))
            if qual:
                target_user.qualifications.append(qual)

        db.session.commit()
        flash(f"Profil für {target_user.firstname} {target_user.lastname} erfolgreich aktualisiert!", "success")
        return redirect(url_for("employee.list_employees"))

    # Alle verfügbaren Qualifikationen für die Checkboxen laden
    qualifications = db.session.scalars(db.select(Qualification)).all()

    return render_template(
        "employee/edit_employee.html",
        target_user=target_user,
        qualifications=qualifications
    )

