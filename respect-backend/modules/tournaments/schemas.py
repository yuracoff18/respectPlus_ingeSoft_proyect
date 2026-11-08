from datetime import datetime, timezone
from typing import Literal
from pydantic import Field, field_validator, model_validator
from core.config import GAMES
from core.schemas import CleanModel


class NewTournament(CleanModel):
    title: str = Field(min_length=4, max_length=80)
    game: str
    description: str = Field(min_length=20, max_length=2000)
    prize: str = Field(min_length=1, max_length=60, default="Por la gloria")
    capacity: Literal[4, 8, 16, 32, 64]
    starts_at: datetime
    region: str = Field(min_length=2, max_length=60, default="Latinoamérica")
    mode: Literal["solo", "team"] = "solo"
    team_size: int = Field(default=1, ge=1, le=10)

    @field_validator("game")
    @classmethod
    def known_game(cls, value):
        if value not in GAMES:
            raise ValueError("Selecciona un juego disponible")
        return value

    @field_validator("starts_at")
    @classmethod
    def future_date(cls, value):
        if value.tzinfo is None or value <= datetime.now(timezone.utc):
            raise ValueError("Elige una fecha futura con zona horaria")
        return value

    @model_validator(mode="after")
    def mode_size(self):
        if self.mode == "solo":
            self.team_size = 1
        elif self.team_size < 2:
            raise ValueError("Un torneo por equipos necesita al menos 2 jugadores por plantilla")
        return self


class JoinRequest(CleanModel):
    team_id: str | None = Field(default=None, max_length=80)
    roster: list[str] | None = Field(default=None, max_length=10)


class Score(CleanModel):
    score_a: int = Field(ge=0, le=999)
    score_b: int = Field(ge=0, le=999)
