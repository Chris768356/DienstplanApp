from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """
    Dieser Decorator prüft, ob der aktuell eingeloggte User die Rolle 'Admin' hat.
    Wenn nicht, wird der Zugriff blockiert.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Prüfen, ob User auf Rolle UND ob "Admin" ist
        if not current_user.user_data.role or current_user.user_data.role.description != "Admin":
            flash("Zugriff verweigert: Dieser Bereich ist nur für Administratoren zugänglich.", "error")
            return redirect(url_for("profile.profile"))
            
        return f(*args, **kwargs)
    return decorated_function

def planer_or_admin_required(f):
    """Prüft, ob der User entweder 'Planer' oder 'Admin' ist."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Wenn die Rolle NICHT Admin und NICHT Planer ist -> Rauswurf
        if not current_user.user_data.role or current_user.user_data.role.description not in ["Admin", "Planer"]:
            flash("Zugriff verweigert: Nur Planer und Administratoren dürfen den Dienstplan bearbeiten.", "error")
            return redirect(url_for("profile.profile"))
            
        return f(*args, **kwargs)
    return decorated_function

def company_required(f):
    """Prüft, ob der User einer Firma zugewiesen ist (oder Admin ist)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Sicherer Abruf
        user_data = getattr(current_user, 'user_data', None)
        role = user_data.role.description if user_data and user_data.role else None
        
        # Admins dürfen durch, auch ohne Firma. Alle anderen brauchen eine company_id.
        if role != "Admin" and (not user_data or not user_data.company_id):
            flash("Du bist noch keiner Firma zugewiesen. Bitte wende dich an deinen Admin.", "error")
            return redirect(url_for("profile.profile"))
            
        return f(*args, **kwargs)
    return decorated_function
