from pydantic import BaseModel, ConfigDict, Field, field_validator
from core.config import GAMES


class CleanModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class GamePreferences(CleanModel):
    games: list[str] = Field(default_factory=list, max_length=6)

    @field_validator("games")
    @classmethod
    def known_games(cls, values):
        if any(value not in GAMES for value in values):
            raise ValueError("Selecciona juegos disponibles")
        return list(dict.fromkeys(values))
