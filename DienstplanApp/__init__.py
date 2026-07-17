from flask import Flask, render_template



def create_app(test_config = None):
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY='dev'
    )
    
    if test_config is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_mapping(test_config)


    @app.route("/")
    def index():
        return render_template("index.html")
    

    return app
 