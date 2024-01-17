import csv
import os
from typing import TypedDict
from flask import Flask, abort, request
from sqlalchemy import func, select
from db_config import GeneratorPrompt, GeneratorPromptInfo, PromptTag, User, db

app = Flask(__name__)

MAXCLACK_DATABASE_URL = os.environ["MAXCLACK_DATABASE_URL"]
MAXCLACK_DATABASE_USERNAME = os.environ["MAXCLACK_DATABASE_USERNAME"]
MAXCLACK_DATABASE_PASSWORD = os.environ["MAXCLACK_DATABASE_PASSWORD"]
MAXCLACK_DATABASE_NAME = os.environ["MAXCLACK_DATABASE_NAME"]

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{
    MAXCLACK_DATABASE_USERNAME}:{MAXCLACK_DATABASE_PASSWORD}@{MAXCLACK_DATABASE_URL}/{MAXCLACK_DATABASE_NAME}"

db.init_app(app)


class PromptResponse(TypedDict):
    prompt: GeneratorPromptInfo


@app.get('/prompt/random')
def get_random_prompt() -> PromptResponse:
    tags = request.args.getlist('tag')

    # make sure user doesnt input a billion tags
    if len(tags) > 20:
        abort(413, 'Too many tags inputted to filter by')

    stmt = select(GeneratorPrompt).order_by(func.random())

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
        abort(204)

    prompt = row.t[0]

    return {
        'prompt': prompt.to_dict()
    }


@app.post('/prompt')
def create_prompt() -> PromptResponse:
    json = request.json

    if not isinstance(json, GeneratorPromptInfo):
        abort(400, "POST '/prompt' body must contain format:" + str(
              GeneratorPromptInfo.__annotations__))

    # TODO: make sure they don't input 20 billion tags
    if len(json.get('tags', [])) > 20:
        abort(413, "POST '/prompt' body contains too many tags")

    username = json.get('creator')
    if username:
        maybe_user = db.session.execute(
            select(User).where(User.username == username)
        ).first()

        if maybe_user is None:
            abort(400, 'No such user exists')

        creator = maybe_user.t[0]
    else:
        creator = None

    tags = PromptTag.get_or_create_all(tag_names)

    prompt = GeneratorPrompt(json['text'], tags=tags, creator=creator)

    db.session.add(prompt)

    db.session.commit()

    return PromptResponse(prompt=prompt.to_dict())


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

                tags: list[PromptTag] = PromptTag.get_or_create_all(tag_names)

                db.session.add(GeneratorPrompt(
                    text, True, tags))

        db.session.commit()
