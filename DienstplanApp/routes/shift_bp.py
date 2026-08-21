from datetime import date, datetime, timedelta

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
    """Zeigt alle zugewiesenen Schichten mit dynamischem Filter an."""
    user_data = getattr(current_user, 'user_data', None)
    role = user_data.role.description if user_data and user_data.role else None
    my_company_id = user_data.company_id if user_data else None
    my_user_id = user_data.id if user_data else None

    # 1. Filter-Parameter aus der URL abfangen (request.args statt request.form bei GET)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    department_id = request.args.get('department_id')
    filter_user_id = request.args.get('user_id')

    # 2. Grundabfrage aufbauen (Wir starten mit der Basis und hängen Filter an)
    query = db.select(Shift)

    # Rollen-Rechte anwenden
    if role == 'Admin':
        pass # Admin darf alles filtern
    elif not my_company_id:
        query = query.where(False) # Kein Zugriff
    elif role == 'Planer':
        # Planer sieht nur Schichten seiner eigenen Firma
        query = query.join(Department).where(Department.company_id == my_company_id)
    elif role == 'Mitarbeiter':
        # Mitarbeiter sieht hart codiert nur sich selbst
        query = query.where(Shift.user_id == my_user_id)
    else:
        query = query.where(False)

    # 3. Dynamische GET-Filter anwenden (wenn der Nutzer im Formular etwas gewählt hat)
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.where(Shift.shift_date >= start_date)
        except ValueError:
            pass
            
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.where(Shift.shift_date <= end_date)
        except ValueError:
            pass

    # Abteilung und Mitarbeiter dürfen nur Planer und Admin filtern
    if role in ['Admin', 'Planer']:
        if department_id:
            query = query.where(Shift.department_id == int(department_id))
        if filter_user_id:
            query = query.where(Shift.user_id == int(filter_user_id))

    # 4. Abfrage ausführen
    query = query.order_by(Shift.shift_date)
    shifts = db.session.scalars(query).all()

    # Kollisionsprüfung für die Ansicht (Krankheits-Icons)
    for shift in shifts:
        absence = db.session.scalar(
            db.select(Absence).where(
                Absence.user_id == shift.user_id,
                Absence.start_date <= shift.shift_date,
                Absence.end_date >= shift.shift_date
            )
        )
        shift.current_absence = absence 
        
    # 5. Listen für die Filter-Dropdowns ins Template laden
    filter_depts = []
    filter_users = []
    
    if role == 'Admin':
        filter_depts = db.session.scalars(db.select(Department)).all()
        filter_users = db.session.scalars(db.select(User)).all()
    elif role == 'Planer':
        filter_depts = db.session.scalars(db.select(Department).where(Department.company_id == my_company_id)).all()
        filter_users = db.session.scalars(db.select(User).where(User.company_id == my_company_id)).all()

    return render_template(
        "shift/list_shifts.html", 
        shifts=shifts, 
        filter_depts=filter_depts, 
        filter_users=filter_users,
        current_filters=request.args # Wir übergeben die gewählten Filter ans HTML zurück
    )


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


@shift_bp.route("/delete/<int:shift_id>", methods=["POST"])
@login_required
@company_required
@planer_or_admin_required
def delete_shift(shift_id):
    """Löscht eine bestehende Schicht sicher aus der Datenbank."""
    shift = db.session.get(Shift, shift_id)
    
    if not shift:
        flash("Schicht nicht gefunden.", "error")
        return redirect(url_for("shift.list_shifts"))

    # Sicherheits-Check: Gehört die Schicht wirklich zur Firma des Planers?
    user_data = getattr(current_user, 'user_data', None)
    role = user_data.role.description if user_data and user_data.role else None
    my_company_id = user_data.company_id if user_data else None

    # Der Admin darf alles löschen. Der Planer nur Schichten seiner Firma.
    if role != 'Admin':
        if shift.department.company_id != my_company_id:
            flash("Sicherheitswarnung: Du kannst nur Schichten deiner eigenen Firma löschen!", "error")
            return redirect(url_for("shift.list_shifts"))

    # Wenn alles passt: Schicht löschen
    db.session.delete(shift)
    db.session.commit()
    
    flash("Die Schicht wurde erfolgreich gelöscht.", "success")
    return redirect(url_for("shift.list_shifts"))


@shift_bp.route("/weekly")
@login_required
@company_required
def weekly_plan():
    """Wochenansicht (Plantafel) für Schichten."""
    user_data = current_user.user_data
    role = user_data.role.description if user_data and user_data.role else "Mitarbeiter"
    my_company_id = user_data.company_id
    my_department_id = user_data.department_id

    # 1. Datum der anzuzeigenden Woche bestimmen (Standard: heute)
    target_date_str = request.args.get("date")
    if target_date_str:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    else:
        target_date = date.today()

    # Montag (0) bis Sonntag (6) der ausgewählten Woche berechnen
    start_of_week = target_date - timedelta(days=target_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Eine Liste mit den 7 Tagen der Woche für den Tabellenkopf
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]

    # Mitarbeiter laden (Rechte-Prüfung!)
    department_filter = request.args.get("department_id")
    user_query = db.select(User)
    
    if role == "Admin":
        # Admin sieht alles, kann nach Abteilung filtern
        if department_filter:
            user_query = user_query.where(User.department_id == department_filter)
    elif role == "Planer":
        # Planer sieht nur SEINE Firma, kann nach Abteilung filtern
        user_query = user_query.where(User.company_id == my_company_id)
        if department_filter:
            user_query = user_query.where(User.department_id == department_filter)
    else:
        # Mitarbeiter sieht nur SEINE EIGENE Abteilung
        user_query = user_query.where(User.department_id == my_department_id)

    users = db.session.scalars(user_query.order_by(User.lastname)).all()
    user_ids = [u.id for u in users]

    # Schichten für diese Woche und diese Mitarbeiter laden
    shifts = []
    if user_ids:
        shift_query = db.select(Shift).where(
            Shift.user_id.in_(user_ids),
            Shift.shift_date >= start_of_week,
            Shift.shift_date <= end_of_week
        )
        shifts = db.session.scalars(shift_query).all()

    # Die Matrix bauen: dictionary -> user_id -> date -> [Schichten]
    schedule_matrix = {u.id: {d: [] for d in week_dates} for u in users}
    for shift in shifts:
        # +++ Qualifikationsprüfung +++
        # Wir wandeln die Listen in "Sets" um. So können wir einfach die Differenz berechnen.
        required_skills = set(shift.shift_type.qualifications)
        user_skills = set(shift.user.qualifications)
        
        # Wenn Fähigkeiten gefordert sind, die der User nicht hat, bleibt etwas übrig
        missing_skills = required_skills - user_skills
        shift.has_missing_skills = len(missing_skills) > 0

        if shift.user_id in schedule_matrix and shift.shift_date in schedule_matrix[shift.user_id]:
            schedule_matrix[shift.user_id][shift.shift_date].append(shift)


    # +++ Kollisionsprüfung (Überschneidungen finden) +++
    for user_id, days in schedule_matrix.items():
        for day, day_shifts in days.items():
            # Nur prüfen, wenn es mehr als 1 Schicht an diesem Tag gibt
            if len(day_shifts) > 1:
                # Schichten nach Startzeit sortieren
                day_shifts.sort(key=lambda s: s.shift_start)
                
                for i in range(len(day_shifts) - 1):
                    current_s = day_shifts[i]
                    next_s = day_shifts[i+1]
                    
                    # Wenn die nächste Schicht anfängt, BEVOR die aktuelle aufhört -> Überschneidung!
                    if next_s.shift_start < current_s.shift_end:
                        # Wir heften dynamisch ein temporäres Attribut an das Objekt
                        current_s.has_collision = True
                        next_s.has_collision = True

    # Abteilungen für den Dropdown-Filter laden (nur für Planer/Admin)
    departments = []
    if role in ["Admin", "Planer"]:
        dept_query = db.select(Department)
        if role == "Planer":
            dept_query = dept_query.where(Department.company_id == my_company_id)
        departments = db.session.scalars(dept_query).all()

    # Blätter-Buttons (Vorherige/Nächste Woche)
    prev_week = start_of_week - timedelta(days=7)
    next_week = start_of_week + timedelta(days=7)

    return render_template(
        "shift/weekly_plan.html",
        users=users,
        week_dates=week_dates,
        schedule_matrix=schedule_matrix,
        start_of_week=start_of_week,
        end_of_week=end_of_week,
        departments=departments,
        current_department=department_filter,
        prev_week=prev_week,
        next_week=next_week
    )
