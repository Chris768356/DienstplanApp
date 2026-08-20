from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from DienstplanApp.extensions import db
from DienstplanApp.models.company import Company
from DienstplanApp.models.department import Department

company_bp = Blueprint("company", __name__)

@company_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_company():
    """Formular zum Erstellen einer neuen Firma mit allen Model-Feldern."""
    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        address = request.form.get("address", "").strip()
        street = request.form.get("street", "").strip()
        house_number = request.form.get("house_number", "").strip()
        zip_code = request.form.get("zip_code", "").strip()
        city = request.form.get("city", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()

        if len(company_name) < 2:
            flash("Der Firmenname muss mindestens 2 Zeichen lang sein.", "error")
            return redirect(url_for("company.create_company"))

        # Neue Firma mit allen Feldern aus deiner company.py anlegen
        new_company = Company(
            company_name=company_name,
            address=address if address else None,
            street=street if street else None,
            house_number=house_number if house_number else None,
            zip_code=zip_code if zip_code else None,
            city=city if city else None,
            phone=phone if phone else None,
            email=email if email else None
        )
        db.session.add(new_company)
        db.session.commit()
        
        flash(f"Firma '{company_name}' wurde erfolgreich angelegt!", "success")
        return redirect(url_for("company.add_department", company_id=new_company.id))

    return render_template("company/create_company.html")


@company_bp.route("/<int:company_id>/add_department", methods=["GET", "POST"])
@login_required
def add_department(company_id):
    """Formular zum Hinzufügen von Abteilungen zu einer bestimmten Firma."""
    company = db.session.get(Company, company_id)
    
    if not company:
        flash("Firma nicht gefunden.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        department_name = request.form.get("department_name", "").strip()

        if len(department_name) < 2:
            flash("Der Abteilungsname muss mindestens 2 Zeichen lang sein.", "error")
            return redirect(url_for("company.add_department", company_id=company.id))

        new_dept = Department(department_name=department_name, company_id=company.id)
        db.session.add(new_dept)
        db.session.commit()

        flash(f"Abteilung '{department_name}' wurde zur Firma '{company.company_name}' hinzugefügt!", "success")
        return redirect(url_for("company.add_department", company_id=company.id))

    # Wir übergeben die Firma an das Template, um den Namen anzuzeigen
    # und eine Liste der bereits bestehenden Abteilungen zu laden
    departments = db.session.scalars(db.select(Department).filter_by(company_id=company.id)).all()
    
    return render_template("company/add_department.html", company=company, departments=departments)
