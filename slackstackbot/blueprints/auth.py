from flask import Blueprint, make_response, request, render_template, current_app
from slackstackbot import utils

import requests

auth = Blueprint("auth", __name__, None)

@auth.route("/install")
def install_app():
    state = request.args.get("state", "")
    code = request.args.get("code", "")

    if state != current_app.config["OAUTH_LOGIN_STATE"] and state != current_app.config["OAUTH_INSTALL_STATE"]:
        return utils.make_error_response("Invalid State")

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
    
    payload = {
        "client_id": current_app.config["SLACK_CLIENT_ID"],
        "client_secret": current_app.config["SLACK_CLIENT_SECRET"],
        "code": code
        }

    r = requests.post("https://slack.com/api/oauth.access", headers=headers, data=payload)
    response = r.json()
    
    if response["ok"] == False:
        return utils.make_error_response("Auth failed")

    if state == current_app.config["OAUTH_INSTALL_STATE"]:
        return install_new_team(response)

    return utils.make_error_response("Not Yet Implemented")

def install_new_team(response):
    (client, collection, state) = utils.get_documentdb_collection()

    # TODO: Must be a way to check for a document without throwing an exception
    try:
        teamState = next((item for item in client.ReadDocuments(collection["_self"]) if item["id"] == response["team_id"]))
        return render_template("welcome.html", team=teamState["name"], url=teamState["configuration"])
    except StopIteration:
        pass

    teamState =  {
        "id": response["team_id"], 
        "name": response["team_name"],
        "configuration": response["incoming_webhook"]["configuration_url"],
        "channel": response["incoming_webhook"]["channel_id"],
        "channel_name": response["incoming_webhook"]["channel"], 
        "webhook": response["incoming_webhook"]["url"],
        "token": response["access_token"],
        "bot_user": response["bot"]["bot_user_id"],
        "bot_token": response["bot"]["bot_access_token"],
        "active": True, 
        "subscriptions": { },
        }
    
    client.CreateDocument(collection["_self"], teamState)
    return render_template("welcome.html", team=teamState["name"], url=teamState["configuration"])
