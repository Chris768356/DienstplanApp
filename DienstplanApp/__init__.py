from flask import Flask, render_template
from DienstplanApp.extensions import db , migrate


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

    ###### Routen u. Blueprints #########
    @app.route("/")
    def index():
        return render_template("index.html")
    
    from DienstplanApp.routes.auth_bp import auth 
    app.register_blueprint(auth, url_prefix="/auth")
    
    ####### Modelle laden ############
    from DienstplanApp.models.user_login import User_login
    from DienstplanApp.models.role import Role
    from DienstplanApp.models.user import User
    from DienstplanApp.models.company import Company
    from DienstplanApp.models.department import Department

    return app
 