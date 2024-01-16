import csv
import os

from flask import Flask, abort, request
from sqlalchemy import func, select
from db_config import GeneratorPrompt, PromptTag, db

app = Flask(__name__)

MAXCLACK_DATABASE_URL = os.environ["MAXCLACK_DATABASE_URL"]
MAXCLACK_DATABASE_USERNAME = os.environ["MAXCLACK_DATABASE_USERNAME"]
MAXCLACK_DATABASE_PASSWORD = os.environ["MAXCLACK_DATABASE_PASSWORD"]
MAXCLACK_DATABASE_NAME = os.environ["MAXCLACK_DATABASE_NAME"]

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{
    MAXCLACK_DATABASE_USERNAME}:{MAXCLACK_DATABASE_PASSWORD}@{MAXCLACK_DATABASE_URL}/{MAXCLACK_DATABASE_NAME}"

db.init_app(app)


@app.get('/prompt/random')
def get_random_prompt():
    tags = request.args.getlist('tag')

    # make sure user doesnt input a billion tags
    if len(tags) > 20:
        abort(413, 'Too many tags inputted to filter by')

    stmt = select(GeneratorPrompt.text).order_by(func.random())

    if not tags:
        stmt = stmt.where(
            GeneratorPrompt.chooseable_in_random == True)
    else:
        # where all of the tags in tags
        # appear in GeneratorPrompt.tags
        stmt = stmt.where(
            *(GeneratorPrompt.tags.any(name=tag)
              for tag in tags)
        )

    row = db.session.execute(stmt).first()

    if row is None:
        return '', 204

    result = row[0]

    return result


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
