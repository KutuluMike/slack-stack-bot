from slackstackbot import app

if __name__ == "__main__":
    import os

    try:
        PORT = int(os.environ.get("HTTP_PLATFORM_PORT ", "5555"))
    except ValueError:
        PORT = 5555
    app.run("0.0.0.0", PORT)
