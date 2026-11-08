from typing import Literal
from pydantic import Field
from core.schemas import CleanModel


class NewReport(CleanModel):
    target_type: Literal["player", "team", "sponsor"]
    target_id: str = Field(min_length=1, max_length=80)
    publication_id: str | None = Field(default=None, max_length=80)
    category: Literal["acoso", "odio", "spam", "suplantacion", "trampas", "otro"]
    reason: str = Field(min_length=10, max_length=1500)
