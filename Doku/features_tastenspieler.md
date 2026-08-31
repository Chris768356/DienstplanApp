# 🚀 Features & Bugfixes (Branch: `tastenspieler` vs. `dev`)

Diese Übersicht fasst die wichtigsten Änderungen und Ergänzungen zusammen, die auf dem Branch `tastenspieler` im Vergleich zum gemeinsamen Entwicklungsstand `dev` vorgenommen wurden.

---

## 1. Profil-Verwaltung fertiggestellt & stabilisiert
* **Speicher-Logik implementiert:** Die Controller-Logik zum Aktualisieren der Profildaten in der Datenbank (`db.session.commit()`) inklusive Transaktionssicherung (`db.session.rollback()`) ausprogrammiert (fehlte auf `dev` komplett).
* **Jinja-Absturzursachen behoben:** Sicherer Zugriff auf Firmen- und Abteilungsbeziehungen (`current_user.user_data.company.name`) im Template, um `NoneType`-Serverfehler bei unvollständigen Profilen zu verhindern.
* **Formular-Verbindung & CSRF-Schutz:** Das Bearbeitungsformular korrekt mit der POST-Route verknüpft und den CSRF-Token eingebunden.

## 2. Kernfeature „Dienstplan-Ansicht“ (Mitarbeiter)
* **Neu erstellt:** Blueprint (`roster_bp.py`) und HTML-Template (`roster.html`) zur live-Abfrage und tabellarischen Darstellung der zugewiesenen Schichten eines angemeldeten Benutzers aus der Datenbank.
* **Navigation:** Link zur Dienstplan-Ansicht in die globale Navigationsleiste (`base.html`) integriert.

## 3. Datenbank-Robustheit & Bugfixes
* **Migration für Nullability:** Migrationsdatei erstellt, damit Registrierungen ohne direkte Zuweisung einer Firma/Abteilung nicht mehr die Datenbank crashen (`company_id` und `department_id` in `user` auf `nullable=True` gesetzt).
* **Kritischen Bug behoben:** Datentyp-Fehler in `absence.py` repariert (`db.boolean` -> `db.Boolean`), der Abstürze bei Tabellen-Operationen verhinderte.
* **DB-Timeout-Prevention:** Datenbank-Verbindungseinstellungen (`pool_recycle=280` und `pool_pre_ping=True`) in `config.py` hinzugefügt, um Verbindungsabbrüche mit MariaDB/XAMPP abzufangen.

## 4. Projektdokumentation & ER-Modell
* **Doku komplettiert:** Die Datei `Doku/doku.md` korrigiert und um die neue Projekt- und Verzeichnisstruktur erweitert.
* **ER-Diagramm:** Interaktives Mermaid-Datenbankschema zur Visualisierung aller Tabellenbeziehungen für das Team hinzugefügt.
