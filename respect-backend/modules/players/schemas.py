from pydantic import Field, field_validator, model_validator
from core.config import GAMES
from core.schemas import GamePreferences


class Profile(GamePreferences):
    name: str = Field(min_length=2, max_length=40)
    headline: str = Field(max_length=120)
    bio: str = Field(max_length=1000)
    game: str
    country: str = Field(min_length=2, max_length=60)
    available: bool

    @field_validator("game")
    @classmethod
    def known_game(cls, value):
        if value not in GAMES:
            raise ValueError("Selecciona un juego disponible")
        return value

    @model_validator(mode="after")
    def include_primary(self):
        self.games = list(dict.fromkeys([self.game, *self.games]))
        return self
