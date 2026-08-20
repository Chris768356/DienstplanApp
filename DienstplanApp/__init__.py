from flask import Flask, render_template
from flask_wtf.csrf import CSRFError

from DienstplanApp.extensions import csrf, db, limiter, login_manager, migrate


def create_app(test_config = None):
    app = Flask(__name__)

    ####### Config laden ############
    app.config.from_mapping(
        SECRET_KEY='dev'
    )
    
    if test_config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_mapping(test_config)

    ###### Initialisierungen #########
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"                                                      # Leitet unangemeldete Nutzer hierhin um
    login_manager.login_message = "Bitte logge dich ein, um diese Seite zu sehen."               # Optionale Flash-Nachricht

    limiter.init_app(app)

    ###### Routen u. Blueprints #########
    @app.route("/")
    def index():
        return render_template("index.html")
    
    from DienstplanApp.routes.auth_bp import auth
    app.register_blueprint(auth, url_prefix="/auth")

    from DienstplanApp.routes.profile_bp import profile_bp
    app.register_blueprint(profile_bp, url_prefix="/profile")

    from DienstplanApp.routes.company_bp import company_bp
    app.register_blueprint(company_bp, url_prefix="/company")

    from DienstplanApp.routes.shift_bp import shift_bp
    app.register_blueprint(shift_bp, url_prefix="/shift")

    from DienstplanApp.routes.absence_bp import absence_bp
    app.register_blueprint(absence_bp, url_prefix="/absence")

    from DienstplanApp.routes.qualification_bp import qualification_bp
    app.register_blueprint(qualification_bp, url_prefix="/qualification")

    from DienstplanApp.routes.role_bp import role_bp
    app.register_blueprint(role_bp, url_prefix="/role")

    from DienstplanApp.routes.info_bp import info_bp
    app.register_blueprint(info_bp)

    ###### Fehlerbehandlung (Error Handlers) #########
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('csrf_error.html', reason=e.description), 400
    
    ####### Modelle laden ############
    from DienstplanApp.models.user_login import User_login
    from DienstplanApp.models.role import Role
    from DienstplanApp.models.user import User
    from DienstplanApp.models.company import Company
    from DienstplanApp.models.department import Department
    from DienstplanApp.models.qualification import Qualification
    from DienstplanApp.models.shift import Shift
    from DienstplanApp.models.shift_type import Shift_Type
    from DienstplanApp.models.absence import Absence

    return app
 