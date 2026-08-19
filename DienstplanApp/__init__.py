from flask import Flask, render_template
from DienstplanApp.extensions import db , migrate, csrf, login_manager, limiter
from flask_wtf.csrf import CSRFError

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
    limiter.init_app(app)

    ###### Routen u. Blueprints #########
    @app.route("/")
    def index():
        return render_template("index.html")
    
    from DienstplanApp.routes.auth_bp import auth 
    app.register_blueprint(auth, url_prefix="/auth")
    
    from DienstplanApp.routes.profile_bp import profile_bp
    app.register_blueprint(profile_bp, url_prefix="/profile")
    
    ####### Modelle laden ############
    from DienstplanApp.models.user_login import User_login
    from DienstplanApp.models.role import Role
    from DienstplanApp.models.user import User
    from DienstplanApp.models.company import Company
    from DienstplanApp.models.department import Department
    from DienstplanApp.models.shift import Shift
    from DienstplanApp.models.shift_type import Shift_Type
    from DienstplanApp.models.qualification import Qualification
    from DienstplanApp.models.user_qualification import User_Qualification
    from DienstplanApp.models.absence import Absence

    
    return app
 