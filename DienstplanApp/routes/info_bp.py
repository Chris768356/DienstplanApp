from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from DienstplanApp.decorators import admin_required
from DienstplanApp.extensions import db
from DienstplanApp.models.ticket import Ticket


info_bp = Blueprint("info", __name__)

@info_bp.route("/impressum")
def impressum():
    return render_template("info/impressum.html")

@info_bp.route("/datenschutz")
def datenschutz():
    return render_template("info/datenschutz.html")

@info_bp.route("/support", methods=["GET", "POST"])
@login_required
def support():
    """Zeigt das Formular für die Nutzer an und speichert die Nachricht."""
    if request.method == "POST":
        message = request.form.get("message", "").strip()
        
        if not message:
            flash("Bitte geben Sie eine Nachricht ein.", "error")
        else:
            new_ticket = Ticket(user_id=current_user.id, message=message)
            db.session.add(new_ticket)
            db.session.commit()
            flash("Deine Nachricht wurde sicher an den Admin übermittelt!", "success")
            return redirect(url_for("index"))
            
    return render_template("info/support.html")

@info_bp.route("/admin/tickets")
@login_required
@admin_required
def admin_tickets():
    """Zeigt dem Admin alle empfangenen Support-Tickets."""
    # Neueste Tickets zuerst laden (absteigend sortiert)
    tickets = db.session.scalars(db.select(Ticket).order_by(Ticket.timestamp.desc())).all()
    return render_template("info/admin_tickets.html", tickets=tickets)

