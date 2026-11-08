from fastapi import HTTPException
from modules.players.services.views import public_user
from store import lock
from core.visibility import is_visible


class SponsorService:
    def __init__(self, repository, teams, players):
        self.repository = repository
        self.teams = teams
        self.players = players

    def view(self, sponsor):
        return {**{key: value for key, value in sponsor.items() if key not in ("moderation_note", "banned_by")}, "owner": public_user(self.players.require(sponsor["owner_id"])), "supported_teams": [{key: value for key, value in self.teams.require(identifier).items() if key != "requests"} for identifier in sponsor["team_ids"] if is_visible(self.repository.store, "teams", self.teams.get(identifier))]}

    def list(self, q="", game=""):
        return [self.view(sponsor) for sponsor in self.repository.active() if (not q or q.casefold() in f"{sponsor['name']} {sponsor['headline']}".casefold()) and (not game or game in sponsor["games"])]

    def profile(self, identifier):
        return self.view(self.repository.require_active(identifier))

    def validate_teams(self, data):
        for identifier in data.team_ids:
            self.teams.require_active(identifier)
        data.team_ids = list(dict.fromkeys(data.team_ids))

    def create(self, data, user):
        raise HTTPException(409 if user.get("account_type") == "sponsor" else 403, "Las empresas se crean mediante el registro de una cuenta Empresa / sponsor. Cada cuenta dispone de su propio perfil.")

    def update(self, identifier, data, user):
        with lock:
            sponsor = self.repository.require_active(identifier)
            if sponsor["owner_id"] != user["id"]:
                raise HTTPException(403, "Solo el propietario puede editar este sponsor.")
            self.validate_teams(data)
            sponsor.update(data.model_dump())
            owner = self.players.require(user["id"])
            if owner.get("account_type") == "sponsor" and owner.get("sponsor_id") == identifier:
                owner.update({key: sponsor[key] for key in ("name", "headline", "bio", "country", "games")})
                owner["game"] = ""
                self.players.save(owner)
            return self.view(self.repository.save(sponsor))
