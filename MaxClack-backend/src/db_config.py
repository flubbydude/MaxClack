import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.sql import func
from typing import TYPE_CHECKING, Any


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
        String(20), unique=True, nullable=False)

    singleplayer_matches: Mapped[list['SingleplayerMatch']] = relationship(
        back_populates='user')

    def __init__(self, username: str):
        self.username = username

    def __repr__(self) -> str:
        return self._repr_helper(username=self.username, id=self.id)


class SingleplayerMatch(BaseModel):
    __tablename__ = 'singleplayer_match'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), nullable=False)

    # text that the player copies while playing the game
    game_text: Mapped[str] = mapped_column(String(2048), nullable=False)
    game_duration_seconds: Mapped[float] = mapped_column(nullable=False)

    user: Mapped['User'] = relationship(back_populates='singleplayer_matches')

    def __init__(self, user: User, game_text: str, game_duration_seconds: float):
        self.user = user
        self.game_text = game_text
        self.game_duration_seconds = game_duration_seconds

    def __repr__(self) -> str:
        return self._repr_helper(user=self.user)
