import csv
import os

from flask import Flask
from db_config import GeneratorPrompt, PromptTag, db

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
    # create tables in the tb if they do not exist
    db.create_all()

    # if generator prompt table is empty,
    # generate prompts from the csv
    if GeneratorPrompt.query.first() is None:
        # populate random prompts with the CSV file
        with open('random_prompts.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                text, *tag_names = row

                # get or create PromptTag
                tags: list[PromptTag] = [PromptTag.query.where(
                    PromptTag.name == tag_name).first() or PromptTag(tag_name) for tag_name in tag_names]

                db.session.add(GeneratorPrompt(
                    text, True, tags))

        db.session.commit()
