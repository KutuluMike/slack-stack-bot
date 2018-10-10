from slackstackbot import app

if __name__ == "__main__":
    import os

    app.run("0.0.0.0", os.environ["PORT"])
