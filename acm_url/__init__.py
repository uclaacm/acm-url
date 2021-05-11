from acm_url.config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import timedelta

# Instantiates the Flask App object
app = Flask(__name__, instance_relative_config=True)

# Setup
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.permanent_session_lifetime = timedelta(minutes=30)

# Import routes once the app exists
from acm_url import schema, routes
