from flask import jsonify
from slackstackbot import utils

class Feeds(object):
    def __init__(self, team, channel):
        (client, collection, state) = utils.get_documentdb_collection()
        
        self.client = client
        self.collection = collection
        self.state = state

        self.team = team
        self.teamState = next((item for item in self.client.ReadDocuments(self.collection["_self"]) if item["id"] == team))

        self.channel = channel

    def help(self):
        response = ("Valid feed commands: list, subscribe, unsubscribe, help.\n"
            "To see the feeds available to your team: `/sefeeds list`\n"
            "To add a feed to this channel: `/sefeeds subscribe <feed_key>`\n"
            "To remove a feed from this channel: `/sefeeds unsubscribe <feed_key>`\n"
            "Custom feeds can be configured in your teams Manage Apps page.")

        return jsonify({ "text" : help })

    def unsubscribe(self, key):
        try:
            feedState = self.state["feeds"][key]
        except KeyError:
            return jsonify({ "text" : "{0} is not a valid feed.".format(key) })

        subs = self.teamState["subscriptions"]
        if key in subs:
            if self.channel in subs[key]:
                subs[key].remove(self.channel)

            if len(subs[key]) == 0:
                del(subs[key])

            self.client.ReplaceDocument(self.teamState["_self"], self.teamState)
            
        if self.team in feedState["teams"]:
            feedState["teams"].remove(self.team)
            self.client.ReplaceDocument(self.state["_self"], self.state)

        return jsonify({ "text" : "Unsbscribed from {0}.".format(key) })

    def subscribe(self, key):
        try:
            feed = self.state["feeds"][key]
        except KeyError:
            return jsonify({ "text" : "{0} is not a valid feed.".format(key) })

        if self.team not in feed["teams"]:
            feed["teams"].append(self.team)
            self.client.ReplaceDocument(self.state["_self"], self.state)

        subs = self.teamState["subscriptions"].get(key)
        if subs is None:
            subs = []

        if not self.channel in subs:
            subs.append(self.channel)
            self.teamState["subscriptions"][key] = subs
            self.client.ReplaceDocument(self.teamState["_self"], self.teamState)

        return jsonify({ "text" : "Subscribed to {0}.".format(key) })

    def list(self):
        results = []
        for key in self.state["feeds"]:
            feed = self.state["feeds"][key]
            if feed["owner"] == "public" or feed["owner"] == self.team:
                subscribed = " *+*" if self.team in feed["teams"] else ""
                results.append("• `{0}`: {1} ({2}){3}".format(key, feed["name"], feed["description"], subscribed))

        return jsonify({ "text" : "The following feeds are available:\n{0}\nUse the feed 'key' to subscribe or unsubscribe from a feed.\n(Feeds you currently subscribe to are marked with a *+*)".format("\n".join(results)) })



