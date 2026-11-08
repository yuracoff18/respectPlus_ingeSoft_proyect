from typing import Literal
from pydantic import Field, model_validator
from core.schemas import GamePreferences


class TeamInput(GamePreferences):
    name: str = Field(min_length=3, max_length=60)
    tag: str = Field(pattern=r"^[A-Za-z0-9]{2,8}$")
    headline: str = Field(min_length=3, max_length=120)
    bio: str = Field(min_length=10, max_length=2000)
    games: list[str] = Field(min_length=1, max_length=6)
    competition_game: str | None = None
    country: str = Field(min_length=2, max_length=60)
    recruiting: bool = True
    max_members: int = Field(default=5, ge=2, le=16)

    @model_validator(mode="after")
    def competition(self):
        self.competition_game = self.competition_game or self.games[0]
        if self.competition_game not in self.games:
            raise ValueError("El juego de competencia debe estar entre las preferencias del equipo")
        return self


class MembershipDecision(GamePreferences):
    decision: Literal["accept", "reject"]
