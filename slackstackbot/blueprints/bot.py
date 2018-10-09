from flask import  Blueprint, current_app, request, jsonify, current_app
from slackstackbot import utils
from slackstackbot.feeds import Feeds

bot = Blueprint("bot", __name__, None)

@bot.route("/feeds", methods=["POST"])
def dispatch_cmd_feeds():
    token = request.form.get("token", "")
    if token != current_app.config["SLACK_COMMAND_TOKEN"]:
        return utils.make_error_response("Command forgery detected: invalid token {0}. Seriously?".format(token))
   
    team = request.form.get("team_id", "")
    channel = request.form.get("channel_id", "")
    feeds = Feeds(team, channel)

    command  = str.split(request.form.get("text", ""))
    if len(command) == 0 or command[0] == "help":
        return feeds.help()

    if command[0] == "list":
        return feeds.list()

    if command[0] == "subscribe":
        return feeds.subscribe(command[1])

    if command[0] == "unsubscribe":
        return feeds.unsubscribe(command[1])

    return jsonify({ "text" : "Sorry, I don't understand {0}. Try `/sefeeds help`".format(command[0]) })
