from flask import Blueprint, render_template

home = Blueprint("home", __name__, None)

@home.route("/")
def render_home():
    return render_template("home.html")

@home.route("/about")
def render_about():
    return render_template("about.html")

@home.route("/help")
def render_help():
    return render_template("help.html")

@home.route("/privacy")
def render_privacy():
    return render_template("privacy.html")


