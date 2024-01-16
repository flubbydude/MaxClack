import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from typing import TYPE_CHECKING, Any, Optional


class _BaseModel(DeclarativeBase):
    def _repr_helper(self, **fields: Any) -> str:
        return f"{self.__class__.__name__}({','.join(f"{key}={val!r}"for key, val in fields.items())})"

    def __repr__(self) -> str:
        if hasattr(self, "id"):
            return self._repr_helper(id=getattr(self, "id"))
        else:
            return super(DeclarativeBase, self).__repr__()


db = SQLAlchemy(model_class=_BaseModel)

# allow me to treat BaseModel = db.Model as a _BaseModel when type checking

if TYPE_CHECKING:
    class ModelAndBase(Model, _BaseModel):
        pass

    BaseModel: type[ModelAndBase]

BaseModel = db.Model  # type: ignore


class User(BaseModel):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(20), unique=True)

    singleplayer_matches: Mapped[list['SingleplayerMatch']] = relationship(
        back_populates='user')

    def __init__(self, username: str):
        self.username = username

    def __repr__(self) -> str:
        return self._repr_helper(username=self.username, id=self.id)


class PromptTagAssociation(BaseModel):
    __tablename__ = 'prompt_tag_association'

    prompt_id = mapped_column(ForeignKey(
        'generator_prompt.id'), primary_key=True)
    tag_id = mapped_column(ForeignKey('prompt_tag.id'), primary_key=True)


GENPROMPT_REPR_LEN = 30


class GeneratorPrompt(BaseModel):
    """Table containing prompts that were sent to ChatGPT to create GameTexts"""

    __tablename__ = 'generator_prompt'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(2048))
    chooseable_in_random: Mapped[bool] = mapped_column(index=True)

    game_texts: Mapped[list['GameText']] = relationship(
        back_populates='generator_prompt')

    tags: Mapped[list['PromptTag']] = relationship(
        secondary='prompt_tag_association', back_populates='prompts')

    def __init__(self, text: str, chooseable_in_random: bool = False, tags: Optional[list['PromptTag']] = None):
        self.text = text
        self.chooseable_in_random = chooseable_in_random
        self.tags = tags if tags is not None else []

    def __repr__(self) -> str:
        if len(self.text) > GENPROMPT_REPR_LEN:
            temp_text = self.text[:GENPROMPT_REPR_LEN] + '...'
        else:
            temp_text = self.text

        return self._repr_helper(text=temp_text)


class PromptTag(BaseModel):
    __tablename__ = 'prompt_tag'

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(1028))

    prompts: Mapped[list['GeneratorPrompt']] = relationship(
        secondary='prompt_tag_association', back_populates='tags')

    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description


GAMETEXT_REPR_LEN = 30


class GameText(BaseModel):
    __tablename__ = 'game_text'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(2048))
    generator_prompt_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('generator_prompt.id'))

    generator_prompt: Mapped[Optional[GeneratorPrompt]
                             ] = relationship(back_populates='game_texts')

    singleplayer_matches: Mapped[list['SingleplayerMatch']] = relationship(
        back_populates='game_text')

    def __repr__(self) -> str:
        if len(self.text) > GAMETEXT_REPR_LEN:
            temp_text = self.text[:GAMETEXT_REPR_LEN] + '...'
        else:
            temp_text = self.text

        return self._repr_helper(text=temp_text, source=self.generator_prompt)


class SingleplayerMatch(BaseModel):
    __tablename__ = 'singleplayer_match'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    game_text_id: Mapped[int] = mapped_column(ForeignKey('game_text.id'))
    timestamp: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now())

    game_duration_seconds: Mapped[float]

    user: Mapped['User'] = relationship(back_populates='singleplayer_matches')

    # text that the player copies while playing the game
    game_text: Mapped['GameText'] = relationship(
        back_populates='singleplayer_matches')

    def __init__(self, user: User, game_text: 'GameText', game_duration_seconds: float):
        self.user = user
        self.game_text = game_text
        self.game_duration_seconds = game_duration_seconds

    def __repr__(self) -> str:
        return self._repr_helper(user=self.user)
