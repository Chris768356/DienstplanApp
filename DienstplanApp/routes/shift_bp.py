from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from DienstplanApp.decorators import (
    admin_required,
    company_required,
    planer_or_admin_required,
)
from DienstplanApp.extensions import db
from DienstplanApp.models.absence import Absence
from DienstplanApp.models.department import Department
from DienstplanApp.models.qualification import Qualification
from DienstplanApp.models.shift import Shift
from DienstplanApp.models.shift_type import Shift_Type
from DienstplanApp.models.user import User

shift_bp = Blueprint("shift", __name__)

@shift_bp.route("/type/create", methods=["GET", "POST"])
@login_required
@company_required
@planer_or_admin_required
def create_shift_type():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        start_str = request.form.get("start", "").strip()
        end_str = request.form.get("end", "").strip()

        # Checkbox-Werte abfangen (als Liste)
        qual_ids = request.form.getlist("qualifications")

        if not name or not start_str or not end_str:
            flash("Bitte füllen Sie alle Felder aus.", "error")
            return redirect(url_for("shift.create_shift_type"))

        try:
            # Zeiten umwandeln
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
        except ValueError:
            flash("Ungültiges Zeitformat.", "error")
            return redirect(url_for("shift.create_shift_type"))

        # Schichtart erstellen (ohne qualification_id!)
        new_shift_type = Shift_Type(name=name, start=start_time, end=end_time)
        
        # Qualifikationen aus der DB laden und anhängen
        for q_id in qual_ids:
            qual = db.session.get(Qualification, int(q_id))
            if qual:
                new_shift_type.qualifications.append(qual)

        # Speichern
        db.session.add(new_shift_type)
        db.session.commit()

        flash(f"Schichtart '{name}' erfolgreich angelegt!", "success")
        return redirect(url_for("shift.create_shift_type"))

    shift_types = db.session.scalars(db.select(Shift_Type)).all()
    qualifications = db.session.scalars(db.select(Qualification)).all()
    return render_template("shift/create_shift_type.html", shift_types=shift_types, qualifications=qualifications)


@shift_bp.route("/assign", methods=["GET", "POST"])
@login_required
@company_required
@planer_or_admin_required
def assign_shift():
    user_data = getattr(current_user, 'user_data', None)
    role = user_data.role.description if user_data and user_data.role else None
    my_company_id = user_data.company_id if user_data else None

    if request.method == "POST":
        user_id = request.form.get("user_id")
        department_id = request.form.get("department_id")
        shift_type_id = request.form.get("shift_type_id")
        shift_date_str = request.form.get("shift_date")

        if not all([user_id, department_id, shift_type_id, shift_date_str]):
            flash("Bitte alle Felder ausfüllen.", "error")
            return redirect(url_for("shift.assign_shift"))

        try:
            shift_date = datetime.strptime(shift_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Ungültiges Datum.", "error")
            return redirect(url_for("shift.assign_shift"))

        collision = db.session.scalar(
            db.select(Absence).where(
                Absence.user_id == int(user_id),
                Absence.start_date <= shift_date,
                Absence.end_date >= shift_date
            )
        )
        if collision:
            flash(f"Achtung: Kollision! Der Mitarbeiter ist an diesem Tag abwesend.", "error")
            return redirect(url_for("shift.assign_shift"))

        shift_type = db.session.get(Shift_Type, int(shift_type_id))
        selected_user = db.session.get(User, int(user_id))
        
        if not shift_type or not selected_user:
            flash("Schichtart oder User nicht gefunden.", "error")
            return redirect(url_for("shift.assign_shift"))

        if shift_type.qualifications:
            for req_qual in shift_type.qualifications:
                if req_qual not in selected_user.qualifications:
                    flash(f"Blockiert: {selected_user.firstname} fehlt die Qualifikation '{req_qual.name}'!", "error")
                    return redirect(url_for("shift.assign_shift"))

        new_shift = Shift(
            department_id=int(department_id),
            shift_type_id=int(shift_type_id),
            user_id=int(user_id),
            shift_date=shift_date,
            shift_start=shift_type.start,
            shift_end=shift_type.end
        )
        db.session.add(new_shift)
        db.session.commit()

        flash("Schicht wurde erfolgreich zugewiesen!", "success")
        return redirect(url_for("shift.assign_shift"))

    # +++ Filtern der Dropdowns für das Frontend +++
    if role == 'Admin':
        users = db.session.scalars(db.select(User)).all()
        departments = db.session.scalars(db.select(Department)).all()
        shift_types = db.session.scalars(db.select(Shift_Type)).all()
    else:
        users = db.session.scalars(db.select(User).where(User.company_id == my_company_id)).all()
        departments = db.session.scalars(db.select(Department).where(Department.company_id == my_company_id)).all()
        shift_types = db.session.scalars(db.select(Shift_Type).where(Shift_Type.company_id == my_company_id)).all()
    
    return render_template("shift/assign_shift.html", users=users, departments=departments, shift_types=shift_types)


@shift_bp.route("/")
@login_required
@company_required
def list_shifts():
    """Zeigt alle zugewiesenen Schichten (den Dienstplan) in einer Tabelle an, gefiltert nach Rechten."""
    # +++ SICHERER ABFRAGE-BLOCK +++
    user_data = getattr(current_user, 'user_data', None)
    role = user_data.role.description if user_data and user_data.role else None
    my_company_id = user_data.company_id if user_data else None
    my_user_id = user_data.id if user_data else None

    # Rechte-Prüfung
    if role == 'Admin':
        shifts = db.session.scalars(db.select(Shift).order_by(Shift.shift_date)).all()
    elif not my_company_id:
        shifts = [] # Nutzer ohne Firma sieht nichts
    elif role == 'Planer':
        shifts = db.session.scalars(
            db.select(Shift).join(Department).where(Department.company_id == my_company_id).order_by(Shift.shift_date)
        ).all()
    elif role == 'Mitarbeiter':
        shifts = db.session.scalars(
            db.select(Shift).where(Shift.user_id == my_user_id).order_by(Shift.shift_date)
        ).all()
    else:
        shifts = []
    
    # Kollisionsprüfung für die Anzeige
    for shift in shifts:
        absence = db.session.scalar(
            db.select(Absence).where(
                Absence.user_id == shift.user_id,
                Absence.start_date <= shift.shift_date,
                Absence.end_date >= shift.shift_date
            )
        )
        shift.current_absence = absence 
        
    return render_template("shift/list_shifts.html", shifts=shifts)


@shift_bp.route("/edit/<int:shift_id>", methods=["GET", "POST"])
@login_required
@company_required
@planer_or_admin_required
def edit_shift(shift_id):
    """Ermöglicht das manuelle Anpassen der Start- und Endzeit einer Schicht."""
    shift = db.session.get(Shift, shift_id)
    
    if not shift:
        flash("Schicht nicht gefunden.", "error")
        return redirect(url_for("shift.list_shifts"))

    if request.method == "POST":
        start_str = request.form.get("shift_start")
        end_str = request.form.get("shift_end")

        try:
            # überschreiben der alten Zeiten mit den neuen Eingaben
            shift.shift_start = datetime.strptime(start_str, "%H:%M").time()
            shift.shift_end = datetime.strptime(end_str, "%H:%M").time()
            
            db.session.commit()
            flash("Schichtzeiten wurden erfolgreich aktualisiert!", "success")
            return redirect(url_for("shift.list_shifts"))
            
        except ValueError:
            flash("Ungültiges Zeitformat.", "error")
            return redirect(url_for("shift.edit_shift", shift_id=shift.id))

    # +++ Wir suchen nach einer Abwesenheit an genau diesem Schicht-Datum +++
    absence = db.session.scalar(
        db.select(Absence).where(
            Absence.user_id == shift.user_id,
            Absence.start_date <= shift.shift_date,
            Absence.end_date >= shift.shift_date
        )
    )

    return render_template("shift/edit_shift.html", shift=shift, absence=absence)
