import hashlib
import hmac
import secrets
import time
import os
from uuid import uuid4
from fastapi import HTTPException
from core.security import password_hash, set_session
from core.visibility import is_visible
from modules.players.services.views import own_user
from store import lock


class AuthService:
    def __init__(self, repository):
        self.repository = repository

    def register(self, data, response):
        with lock:
            if data.username.casefold() in ("admin", os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin").casefold()):
                raise HTTPException(409, "Ese nombre de usuario está reservado.")
            if self.repository.identity_taken(data.email, data.username):
                raise HTTPException(409, "El correo o el nombre de usuario ya está registrado.")
            user = {"id": str(uuid4()), "email": data.email, "username": data.username.lower(), "name": data.name, "headline": "Mi siguiente nivel empieza aquí", "bio": "", "game": "Valorant", "games": ["Valorant"], "game_profiles": {}, "role": "player", "banned": False, "country": "Colombia", "available": True, "color": secrets.choice(["#c1515d", "#819ed0", "#a791cb", "#7ba99c"]), "connections": [], "password_hash": password_hash(data.password)}
            user["account_type"] = data.account_type
            sponsor = None
            if data.account_type == "sponsor":
                user.update({"sponsor_id": str(uuid4()), "headline": "Empresa / sponsor", "games": [], "game": "", "available": False})
                sponsor = {"id": user["sponsor_id"], "owner_id": user["id"], "name": user["name"], "headline": user["headline"], "bio": "", "country": user["country"], "games": [], "website": "", "team_ids": [], "color": user["color"], "banned": False}
            self.repository.create_account(user, sponsor)
            set_session(self.repository, response, user)
            return own_user(user)

    def login(self, data, response):
        user = self.repository.by_identifier(data.identifier)
        stored = user.get("password_hash") if user else None
        candidate = password_hash(data.password, stored.split(":")[0] if stored else "0" * 32)
        if not stored or not hmac.compare_digest(stored, candidate):
            raise HTTPException(401, "Usuario, correo o contraseña incorrectos.")
        if not is_visible(self.repository.store, "users", user):
            raise HTTPException(403, "Tu cuenta está suspendida.")
        with lock:
            set_session(self.repository, response, user)
        return own_user(user)

    def current(self, token):
        if not token:
            raise HTTPException(401, "Inicia sesión para continuar.")
        identifier = hashlib.sha256(token.encode()).hexdigest()
        session = self.repository.session(identifier)
        if not session or session["expires_at"] < time.time():
            if session:
                self.repository.delete_session(identifier)
            raise HTTPException(401, "Tu sesión expiró. Vuelve a iniciar sesión.")
        user = self.repository.require(session["user_id"])
        if not is_visible(self.repository.store, "users", user):
            raise HTTPException(403, "Tu cuenta está suspendida.")
        return user

    def logout(self, token, response):
        if token:
            self.repository.delete_session(hashlib.sha256(token.encode()).hexdigest())
        response.delete_cookie("respect_session", path="/")
        return {"ok": True}
