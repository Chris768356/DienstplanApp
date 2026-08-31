from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from DienstplanApp.decorators import (
    admin_required,
    company_required,
    planer_or_admin_required,
)
from DienstplanApp.extensions import db
from DienstplanApp.models.qualification import Qualification

qualification_bp = Blueprint("qualification", __name__)

@qualification_bp.route("/create", methods=["GET", "POST"])
@login_required
@company_required
@planer_or_admin_required
def create_qualification():
    """Formular zum Anlegen neuer Qualifikationen für den Katalog."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()

        if len(name) < 2:
            flash("Der Name der Qualifikation muss mindestens 2 Zeichen lang sein.", "error")
            return redirect(url_for("qualification.create_qualification"))

        # Neue Qualifikation in der Datenbank speichern
        new_qual = Qualification(name=name)
        db.session.add(new_qual)
        db.session.commit()

        flash(f"Qualifikation '{name}' wurde erfolgreich angelegt!", "success")
        return redirect(url_for("qualification.create_qualification"))

    # Lade alle bestehenden Qualifikationen für die Übersicht
    qualifications = db.session.scalars(db.select(Qualification).order_by(Qualification.name)).all()
    
    return render_template("qualification/create_qualification.html", qualifications=qualifications)
