from DienstplanApp.extensions import db


class Shift(db.Model):
    __tablename__ = "shift"

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"), nullable=False)
    shift_type_id = db.Column(db.Integer, db.ForeignKey("shift_type.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    shift_date = db.Column(db.Date, nullable=False)
    shift_start = db.Column(db.Time, nullable=False)
    shift_end = db.Column(db.Time, nullable=False)
    department = db.relationship("Department")
    shift_type = db.relationship("Shift_Type")
    user = db.relationship("User")

    @property
    def duration_hours(self):
        """Berechnet die Dauer der Schicht in Dezimalstunden (z.B 8.5) und fängt Nachtschichten ab."""
        if not self.shift_start or not self.shift_end:
            return 0.0
        from datetime import datetime, date, timedelta

        # Beide Zeiten auf dasselbe Pseudodatum heften
        base_date = date.today()
        dt_start = datetime.combine(base_date, self.shift_start)
        dt_end = datetime.combine(base_date, self.shift_end)

        # Nachtschicht abfangen: Wenn die Endzeit vor der Startzeit liegt (z.B. 22:00 bis 06:00)
        if dt_end < dt_start:
            dt_end += timedelta(days=1)

        diff = dt_end - dt_start
        return diff.total_seconds() / 3600.0
