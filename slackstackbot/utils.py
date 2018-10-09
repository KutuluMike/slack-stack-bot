from flask import make_response, current_app
from pydocumentdb import document_client

def get_documentdb_collection():
    credentials = dict([s.split("=", 1) for s in current_app.config["DOCUMENTDB_CONNSTR"].split(";") if s != ""])
    client = document_client.DocumentClient(credentials["AccountEndpoint"], { "masterKey" : credentials["AccountKey"] })

    db = next((item for item  in client.ReadDatabases() if item ["id"] == current_app.config["DOCUMENTDB_DATABASE"]))
    collection = next((item for item in client.ReadCollections(db["_self"]) if item["id"] == current_app.config["DOCUMENTDB_COLLECTION"]))
    state = next((item for item in client.ReadDocuments(collection["_self"]) if item["id"] == "state"))
    
    return (client, collection, state)

def make_error_response(message):
    return make_response(message, 403, { "X-Slack-No-Retry" : 1})