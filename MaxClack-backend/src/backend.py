import csv
import os
from typing import TypedDict
from flask import Flask, abort, request
from sqlalchemy import func, select, or_
from db_config import GeneratorPrompt, GeneratorPromptInfo, GeneratorPromptInfoWithId, PromptTag, User, db

app = Flask(__name__)

MAXCLACK_DATABASE_URL = os.environ["MAXCLACK_DATABASE_URL"]
MAXCLACK_DATABASE_USERNAME = os.environ["MAXCLACK_DATABASE_USERNAME"]
MAXCLACK_DATABASE_PASSWORD = os.environ["MAXCLACK_DATABASE_PASSWORD"]
MAXCLACK_DATABASE_NAME = os.environ["MAXCLACK_DATABASE_NAME"]

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{
    MAXCLACK_DATABASE_USERNAME}:{MAXCLACK_DATABASE_PASSWORD}@{MAXCLACK_DATABASE_URL}/{MAXCLACK_DATABASE_NAME}"

db.init_app(app)


class PromptResponse(TypedDict):
    prompt: GeneratorPromptInfoWithId


@app.get('/prompt/random')
def get_random_prompt() -> PromptResponse:
    """Gets a random GeneratorPrompt from the database,
    specifically one where the field "chooseable_in_random == True".

    Tags may be passed in as
    URL args (for example, "/prompt/random?tag=sports&tag=movies").
    If tags are passed, all of the prompts are searched for a random
    prompt tagged with either sports or movies.

    Returns:
        PromptResponse: The prompt that was found in the database
    """

    tags = request.args.getlist('tag')

    stmt = select(GeneratorPrompt).where(
        GeneratorPrompt.chooseable_in_random == True).order_by(func.random())

    if tags:
        # where all of the tags in tags
        # appear in GeneratorPrompt.tags

        # TODO: idk if this is optimized cuz idk SQL or MySQL well enough.
        # try debugging and checking
        stmt = stmt.where(
            or_(
                *(GeneratorPrompt.tags.any(name=tag)
                  for tag in tags)
            )
        )

    row = db.session.execute(stmt).first()

    if row is None:
        abort(204, "A prompt with the given variables does not exist")

    prompt = row.t[0]

    return PromptResponse(prompt=prompt.to_dict_with_id())


@app.get('/prompt/<int:id>')
def get_prompt_by_id(id: int):
    """Gets the GeneratorPrompt object from the db based on its id.

    Args:
        id (int): The id of the prompt to search for

    Returns:
        PromptResponse: The prompt that was found in the database
    """

    result = db.session.execute(
        select(GeneratorPrompt).where(
            GeneratorPrompt.id == id
        )
    ).first()

    if not result:
        abort(404, "A prompt with the given parameter(s) does not exist")

    prompt = result.t[0]

    return PromptResponse(prompt=prompt.to_dict_with_id())


MAX_TAGS_PER_GENERATOR_PROMPT = 100


@app.post('/prompt')
def create_prompt():
    """Creates a prompt in the database with the given information.

    Returns:
        PromptResponse: The prompt that was created in the database, along with a 201 (created) response code
    """

    json = request.json

    if not isinstance(json, GeneratorPromptInfo):
        abort(400, "POST '/prompt' body must contain format:" + str(
              GeneratorPromptInfo.__annotations__))

    # TODO: make sure they don't input 20 billion tags
    tag_names = json.get('tags')
    if tag_names and len(tag_names) > MAX_TAGS_PER_GENERATOR_PROMPT:
        abort(413, "POST '/prompt' body contains too many tags")

    username = json['creator']
    maybe_user = db.session.execute(
        select(User).where(User.username == username)
    ).first()

    if maybe_user is None:
        abort(400, f'No such user {username!r} exists')

    creator = maybe_user.t[0]

    tags = PromptTag.get_or_create_all(
        tag_names, creator) if tag_names else None

    prompt = GeneratorPrompt(json['text'], tags=tags, creator=creator)

    db.session.add(prompt)

    db.session.commit()

    return PromptResponse(prompt=prompt.to_dict_with_id()), 201


with app.app_context():
    # create tables in the db if they do not exist
    db.create_all()

    # get or create the admin user
    admin_user = User.get_or_create('admin')

    # if generator prompt table is empty,
    # generate prompts from the csv
    # and assign them to the admin user
    if GeneratorPrompt.query.first() is None:
        # populate random prompts with the CSV file
        with open('random_prompts.csv') as f:
            reader = csv.reader(f)
            for row in reader:
                text, *tag_names = row

                tags: list[PromptTag] = PromptTag.get_or_create_all(
                    tag_names, admin_user)

                db.session.add(GeneratorPrompt(
                    text, admin_user, True, tags))

    db.session.commit()
