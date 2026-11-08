from pydantic import Field, field_validator
from core.config import GAMES
from core.schemas import CleanModel
from typing import Literal


class Content(CleanModel):
    content: str = Field(min_length=1, max_length=2000)


class NewPost(Content):
    game: str = Field(default="General", max_length=40)
    publisher_type: Literal["player", "team", "sponsor"] = "player"
    publisher_id: str | None = Field(default=None, max_length=80)

    @field_validator("game")
    @classmethod
    def known_game(cls, value):
        if value not in ["General", *GAMES]:
            raise ValueError("Selecciona un juego disponible")
        return value
