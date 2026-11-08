from pydantic import Field, field_validator
from urllib.parse import urlsplit
from core.schemas import GamePreferences


class SponsorInput(GamePreferences):
    name: str = Field(min_length=3, max_length=60)
    headline: str = Field(min_length=3, max_length=120)
    bio: str = Field(min_length=10, max_length=2000)
    country: str = Field(min_length=2, max_length=60)
    website: str = Field(default="", max_length=300)
    games: list[str] = Field(min_length=1, max_length=6)
    team_ids: list[str] = Field(default_factory=list, max_length=30)

    @field_validator("website")
    @classmethod
    def safe_website(cls, value):
        if value:
            parsed = urlsplit(value)
            if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.username or parsed.password:
                raise ValueError("Usa una dirección web http o https válida")
        return value
