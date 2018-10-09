import json

from flask import  Blueprint, request, make_response, current_app
from slackstackbot import utils

events = Blueprint("events", __name__, None)

@events.route("/listening", methods=["GET", "POST"])
def handle_events():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, { "Content-Type" : "application/json" })

    token = slack_event.get("token", "")
    if token != current_app.config["SLACK_COMMAND_TOKEN"]:
        return utils.make_error_response("Event forgery detected: invalid token {0}. Seriously?".format(token))

    if "event" in slack_event:
        app_id = slack_event.get("api_app_id", "")
        if app_id != current_app.config["API_APP_ID"]:
            return utils.make_error_response("Event received for wrong app: {0}".format(app_id))

        event_type = slack_event["event"]["type"]
        return _dispatch_event(event_type, slack_event)

    return utils.make_error_response("No event metadata found.")

def _dispatch_event(event_type, event_data):
    if event_type == "app_uninstalled":
        team = event_data.get("team_id", "")
        return uninstall_team(team)

    # TODO: Do something meaningful here; right now we only support being fully uninstalled, which
    # is handled by the app_uninstalled event.
    if event_type == "tokens_revoked":
        return make_response("OK", 200)

    return utils.make_error_response("Not subscribed to event type {0}".format(event_type))
    
def uninstall_team(team):
    try:
        (client, collection, state) = utils.get_documentdb_collection()
        teamState = next((item for item in client.ReadDocuments(collection["_self"]) if item["id"] == team))
    except StopIteration:
        return utils.make_error_response("'{0}' is not a valid, installed Slack team ID.".format(team))

    for key in state["feeds"]:
        feedState = state["feeds"][key]
        if team in feedState["teams"]:
            feedState["teams"].remove(team)

    client.ReplaceDocument(state["_self"], state)
    client.DeleteDocument(teamState["_self"])

    return make_response("Team uninstalled", 200)

