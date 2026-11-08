from typing import Literal
from pydantic import Field, field_validator
from core.bootstrap import validate_admin_password
from core.schemas import CleanModel
from modules.auth.schemas import Register


class NewAdmin(Register):
    account_type: Literal["player"] = "player"

    @field_validator("password")
    @classmethod
    def strong_password(cls, value):
        return validate_admin_password(value)


class CaseDecision(CleanModel):
    action: Literal["ban", "dismiss"]
    reason: str = Field(min_length=10, max_length=1500)
    report_ids: list[str] = Field(min_length=1, max_length=500)


class Unban(CleanModel):
    reason: str = Field(min_length=10, max_length=1500)
