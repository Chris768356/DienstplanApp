from flask import Blueprint, request , render_template

auth = Blueprint("auth",__name__)

@auth.route("/register")
def register():
    return render_template("auth/register.html")