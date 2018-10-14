from flask import  Blueprint, flash, redirect, render_template, request, url_for, abort
from slackstackbot import utils

admin = Blueprint("admin", __name__)

@admin.route("/")
def home():
    (client, collection, state) = utils.get_documentdb_collection()
    return render_template("admin/home.html", state=state)

@admin.route("/createfeed", methods=['GET', 'POST'])
def create():
    (client, collection, state) = utils.get_documentdb_collection()

    if request.method == "POST":
        id = request.form["feed_id"]
        site = request.form["site"]
        name = request.form["name"]
        description = request.form["description"]
        uri = request.form["uri"]
        valid = True

        if not id:
            flash("Keed Key is required.")
            valid = False

        if not site:
            flash("Site Identifier is required.")
            valid = False

        if not name:
            flash("Feed Name is required.")
            valid = False

        if not description:
            flash("Feed Description is required.")
            valid = False

        if not uri:
            flash("Source URI is required")
            valid = False

        if valid:
            try:
                existing = state["feeds"][id]
                if existing:
                    flash("Feed Keys must be unique.")
                    valid = False;
            except KeyError:
                pass

        feed = {
            "site": site,
            "name": name,
            "description": description,
            "uri" : uri
        }

        if not valid:
            return render_template("admin/createfeed.html", state=state, feed=feed)

        state["feeds"][id] = feed
        client.ReplaceDocument(state["_self"], state)

        return redirect(url_for(".home"))
    
    return render_template("admin/createfeed.html", state=state)

@admin.route("/editfeed/<id>", methods=['GET', 'POST'])
def edit(id):
    (client, collection, state) = utils.get_documentdb_collection()
    try:
        feed = state["feeds"][id]
    except KeyError:
        abort(404)

    if request.method == "POST":
        feed["site"] = request.form["site"]
        feed["name"] = request.form["name"]
        feed["description"] = request.form["description"]
        feed["uri"] = request.form["uri"]

        state["feeds"][id] = feed
        client.ReplaceDocument(state["_self"], state)

        return redirect(url_for("admin.home"))

    return render_template("admin/editfeed.html", feed=feed, id=id)
