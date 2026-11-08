from pydantic import Field, field_validator
from core.config import GAMES
from core.schemas import CleanModel


class SyncAccount(CleanModel):
    game: str
    identifier: str = Field(min_length=3, max_length=100)
    region: str = Field(default="la1", max_length=15)
    platform: str = Field(default="pc", max_length=15)
    queue: str = Field(default="solo", max_length=30)
    consent: bool

    @field_validator("game")
    @classmethod
    def known_game(cls, value):
        if value not in GAMES:
            raise ValueError("Juego no disponible")
        return value

    @field_validator("consent")
    @classmethod
    def requires_consent(cls, value):
        if not value:
            raise ValueError("Autoriza la consulta y publicación de tus estadísticas")
        return value
