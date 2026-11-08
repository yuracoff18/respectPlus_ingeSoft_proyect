from fastapi import HTTPException
from modules.players.services.views import own_user, public_user
from store import lock


class PlayerService:
    def __init__(self, repository):
        self.repository = repository

    def list(self, q="", game="", rank="", available=False):
        users = [public_user(user) for user in self.repository.active() if user.get("role", "player") == "player" and user.get("account_type", "player") == "player"]
        return [user for user in users if (not q or q.lower() in f"{user['name']} {user['username']} {user['headline']}".lower()) and (not game or game in user["games"]) and (not rank or any((profile.get("current_rank") or "").casefold() == rank.casefold() for name, profile in user["game_profiles"].items() if not game or name == game)) and (not available or user["available"])]

    def profile(self, identifier):
        user = self.repository.find_profile(identifier)
        if user is None or user.get("banned") or user.get("role") == "admin" or user.get("account_type") == "sponsor":
            raise HTTPException(404, "No encontramos este jugador.")
        return public_user(user)

    def update(self, data, user):
        if user.get("account_type") == "sponsor":
            raise HTTPException(403, "Edita tu empresa desde su perfil de sponsor.")
        with lock:
            current = self.repository.require(user["id"])
            current.update(data.model_dump())
            return own_user(self.repository.save(current))

    def connect(self, identifier, user):
        with lock:
            target = self.repository.require_active(identifier)
            current = self.repository.require(user["id"])
            if identifier == current["id"]:
                raise HTTPException(400, "No puedes conectar contigo mismo.")
            connected = identifier not in current["connections"]
            for first, second in [(current, target), (target, current)]:
                if connected:
                    first["connections"] = list(dict.fromkeys([*first["connections"], second["id"]]))
                else:
                    first["connections"] = [value for value in first["connections"] if value != second["id"]]
                self.repository.save(first)
            return own_user(current)
