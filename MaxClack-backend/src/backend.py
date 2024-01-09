import os

from flask import Flask
from db_config import db, User, SingleplayerMatch

app = Flask(__name__)

MAXCLACK_DATABASE_URL = os.environ["MAXCLACK_DATABASE_URL"]
MAXCLACK_DATABASE_USERNAME = os.environ["MAXCLACK_DATABASE_USERNAME"]
MAXCLACK_DATABASE_PASSWORD = os.environ["MAXCLACK_DATABASE_PASSWORD"]
MAXCLACK_DATABASE_NAME = os.environ["MAXCLACK_DATABASE_NAME"]

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{
    MAXCLACK_DATABASE_USERNAME}:{MAXCLACK_DATABASE_PASSWORD}@{MAXCLACK_DATABASE_URL}/{MAXCLACK_DATABASE_NAME}"

db.init_app(app)


@app.get('/')
def hello_world():
    return "Hello, World!"


with app.app_context():
    db.create_all()
