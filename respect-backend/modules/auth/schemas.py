import re
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Login(BaseModel):
    identifier: str = Field(default="", max_length=254)
    email: str | None = Field(default=None, max_length=254)
    password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def login_identifier(self):
        self.identifier = (self.identifier or self.email or "").strip().lower()
        if not self.identifier:
            raise ValueError("Escribe tu usuario o correo electrónico")
        return self


class Register(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    username: str = Field(pattern=r"^[A-Za-z0-9_]{3,24}$")
    name: str = Field(min_length=2, max_length=40)
    account_type: Literal["player", "sponsor"] = "player"

    @field_validator("email")
    @classmethod
    def email_valid(cls, value):
        value = value.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Correo electrónico inválido")
        return value

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        if len(value.strip()) < 2:
            raise ValueError("Escribe tu nombre o el de la empresa")
        return value.strip()

    @model_validator(mode="after")
    def company_name(self):
        if self.account_type == "sponsor" and len(self.name) < 3:
            raise ValueError("El nombre de la empresa debe tener al menos 3 caracteres")
        return self
