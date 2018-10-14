from flask import Flask

from .blueprints.home import home
from .blueprints.bot import bot
from .blueprints.auth import auth
from .blueprints.events import events
from .blueprints.admin import admin

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.Config')
app.config.from_pyfile('config.py')

app.register_blueprint(home)
app.register_blueprint(auth)
app.register_blueprint(events)
app.register_blueprint(bot, url_prefix='/bot')
app.register_blueprint(admin, url_prefix='/admin')

wsgi_app = app.wsgi_app