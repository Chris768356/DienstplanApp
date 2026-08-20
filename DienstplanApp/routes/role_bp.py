from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from DienstplanApp.decorators import admin_required
from DienstplanApp.extensions import db
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
