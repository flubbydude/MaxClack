import os

from flask import Flask
from db_config import db, User

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["MAXCLACK_DATABASE_URI"]

db.init_app(app)


@app.get('/')
def hello_world():
    return "Hello, World!"


with app.app_context():
    db.create_all()
