from acm_url.config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import timedelta

app = Flask(__name__, instance_relative_config=True)

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.permanent_session_lifetime = timedelta(minutes=30)

from acm_url import schema, routes
