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
from DienstplanApp.models.user import User  # +++ NEU: Import für den JOIN +++

absence_bp = Blueprint("absence", __name__)

@absence_bp.route("/new", methods=["GET", "POST"])
@login_required
@company_required
@planer_or_admin_required
def create_absence():
    """Formular zum Eintragen von Urlaub oder Krankheit."""
    if request.method == "POST":
        start_str = request.form.get("start_date")
        end_str = request.form.get("end_date")
        abs_type = request.form.get("type", "").strip()

        if not start_str or not end_str or not abs_type:
            flash("Bitte alle Felder ausfüllen.", "error")
            return redirect(url_for("absence.create_absence"))

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Ungültiges Datumsformat.", "error")
            return redirect(url_for("absence.create_absence"))

        # Logik-Prüfung: Enddatum darf nicht vor Startdatum liegen
        if start_date > end_date:
            flash("Das Enddatum darf nicht vor dem Startdatum liegen.", "error")
            return redirect(url_for("absence.create_absence"))

        # Sicherer Zugriff auf die User-ID
        user_data = getattr(current_user, 'user_data', None)
        if not user_data:
            flash("Fehler beim Laden des Benutzerprofils.", "error")
            return redirect(url_for("absence.list_absences"))

        # Eintragen in die Datenbank
        new_absence = Absence(
            user_id=user_data.id, 
            start_date=start_date,
            end_date=end_date,
            type=abs_type,
            status=True
        )
        db.session.add(new_absence)
        db.session.commit()

        flash("Abwesenheit erfolgreich eingetragen!", "success")
        return redirect(url_for("absence.list_absences"))

    return render_template("absence/create_absence.html")


@absence_bp.route("/")
@login_required
@company_required
def list_absences():
    """Zeigt alle eingetragenen Abwesenheiten an, gefiltert nach Berechtigung."""
    # +++ ABFRAGE-BLOCK +++
    user_data = getattr(current_user, 'user_data', None)
    role = user_data.role.description if user_data and user_data.role else None
    my_company_id = user_data.company_id if user_data else None
    my_user_id = user_data.id if user_data else None

    if role == 'Admin':
        absences = db.session.scalars(db.select(Absence).order_by(Absence.start_date)).all()
    elif not my_company_id:
        absences = []
    elif role == 'Planer':
        # Planer sieht alle Abwesenheiten von Usern aus SEINER Firma
        absences = db.session.scalars(
            db.select(Absence).join(User).where(User.company_id == my_company_id).order_by(Absence.start_date)
        ).all()
    elif role == 'Mitarbeiter':
        # Mitarbeiter sieht nur seine eigenen Abwesenheiten
        absences = db.session.scalars(
            db.select(Absence).where(Absence.user_id == my_user_id).order_by(Absence.start_date)
        ).all()
    else:
        absences = []

    return render_template("absence/list_absences.html", absences=absences)
