from DienstplanApp import create_app
from DienstplanApp.extensions import db
from DienstplanApp.models.role import Role
from DienstplanApp.models.company import Company
from DienstplanApp.models.department import Department
from DienstplanApp.models.shift_type import Shift_Type
from DienstplanApp.models.shift import Shift
from DienstplanApp.models.qualification import Qualification
from DienstplanApp.models.user_login import User_login
from DienstplanApp.models.user import User
from datetime import date, datetime, time

def seed_data():
    app = create_app()
    with app.app_context():
        print("Starte Seeding der Datenbank...")

        # 1. Rollen anlegen
        admin_role = Role.query.filter_by(description="Admin").first()
        if not admin_role:
            admin_role = Role(description="Admin")
            db.session.add(admin_role)
            print("- Rolle 'Admin' erstellt")

        user_role = Role.query.filter_by(description="Benutzer").first()
        if not user_role:
            user_role = Role(description="Benutzer")
            db.session.add(user_role)
            print("- Rolle 'Benutzer' erstellt")

        db.session.commit()

        # 2. Firma anlegen
        company = Company.query.first()
        if not company:
            company = Company(
                company_name="Musterfirma GmbH",
                address="Hauptstraße 123",
                street="Hauptstraße",
                house_number="123",
                zip_code="12345",
                city="Musterstadt",
                phone="01234-567890",
                email="info@musterfirma.de"
        )
            db.session.add(company)
            db.session.commit()

        # 3. Abteilung anlegen
        department = Department.query.first()
        if not department:
            department = Department(
                company_id=company.id,
                department_name="IT-Abteilung"
            )
            db.session.add(department)
            print("-- Abteilung 'IT-Abteilung' erstellt")
            db.session.commit()

        # 4. Qualifikationen anlegen
        qual1 = Qualification.query.filter_by(name="Ersthelfer").first()
        if not qual1:
            qual1 = Qualification(
                company_id=company.id,
                name="Ersthelfer"
            )
            db.session.add(qual1)
            print("- Qualifikation 'Ersthelfer' erstellt")

        qual2 = Qualification.query.filter_by(name="Schichtleiter").first()
        if not qual2:
            qual2 = Qualification(
                company_id=company.id,
                name="Schichtleiter"
            )
            db.session.add(qual2)
            print("- Qualifikation 'Schichtleiter' erstellt")

        db.session.commit()

        # 5. User & User_login anlegen (Admin und Benutzer)
        # Admin-Login & Profildaten
        admin_login = User_login.query.filter_by(email="admin@musterfirma.de").first()
        if not admin_login:
            admin_login = User_login(
                email="admin@musterfirma.de",
                role_id=admin_role.id
            )
            admin_login.set_password("admin123")
            db.session.add(admin_login)
            db.session.commit()

            admin_user = User(
                login_id=admin_login.id,
                company_id=company.id,
                    department_id=department.id,
                    firstname="Max",
                    lastname="Mustermann",
                    role_id=admin_role.id
                )
            db.session.add(admin_user)
            print("- Admin-Benutzer 'Max Mustermann' (admin@musterfirma.de / admin123) erstellt")

        # Standard-Benutzer-Login & Profildaten
        user_login = User_login.query.filter_by(email="user@musterfirma.de").first()
        if not user_login:
            user_login = User_login(
                email="user@musterfirma.de",
                role_id=user_role.id
            )
            user_login.set_password("user123")
            db.session.add(user_login)
            db.session.commit()

            normal_user = User(
                login_id=user_login.id,
                company_id=company.id,
                department_id=department.id,
                firstname="Erika",
                lastname="Mustermann",
                role_id=user_role.id
            )
            db.session.add(normal_user)
            normal_user.qualifications.append(qual1)  # Ersthelfer zuweisen
            print("- Standard-Benutzer 'Erika Mustermann' (user@musterfirma.de / user123) erstellt")

        db.session.commit()

        # 6. Schicht-Typen anlegen
        # Wichtig: Der Klassenname in models/shift_type.py ist Shift_Type (mit großem T)
        st_frueh = Shift_Type.query.filter_by(name="Frühschicht").first()
        print("- Firma 'Musterfirma GmbH' erstellt")
        if not st_frueh:
            st_frueh = Shift_Type(
                company_id=company.id,
                name="Frühschicht",
                start=time(6, 0),
                end=time(14, 0)
            )
            db.session.add(st_frueh)
            print("- Schicht-Typ 'Frühschicht' erstellt")

        st_spaet = Shift_Type.query.filter_by(name="Spätschicht").first()
        if not st_spaet:
            st_spaet = Shift_Type(
                company_id=company.id,
                name="Spätschicht",
                start=time(14, 0),
                end=time(22, 0)
            )
            db.session.add(st_spaet)
            print("- Schicht-Typ 'Spätschicht' erstellt")

        db.session.commit()
        print("Seeding erfolgreich abgeschlossen!")

if __name__ == "__main__":
    seed_data()
