from uuid import uuid4
from fastapi import HTTPException
from modules.players.services.views import public_user
from store import lock
from core.visibility import is_visible


class TeamService:
    def __init__(self, repository, players):
        self.repository = repository
        self.players = players

    def view(self, team):
        roster = [public_user(self.players.get(member)) for member in team["members"] if is_visible(self.repository.store, "users", self.players.get(member))]
        return {**{key: value for key, value in team.items() if key not in ("requests", "moderation_note", "banned_by")}, "rank": "Rangos por juego", "competition_game": team.get("competition_game") or team["games"][0], "members": [member["id"] for member in roster], "captain": public_user(self.players.require(team["owner_id"])), "roster": roster}

    def list(self, q="", game="", rank="", recruiting=False):
        teams = [self.view(team) for team in self.repository.active() if (not q or q.casefold() in f"{team['name']} {team['tag']} {team['headline']}".casefold()) and (not game or game in team["games"]) and (not recruiting or team["recruiting"])]
        return [team for team in teams if not rank or any((member.get("game_profiles", {}).get(game or team["competition_game"], {}).get("current_rank") or "").casefold() == rank.casefold() for member in team["roster"])]

    def profile(self, identifier):
        return self.view(self.repository.require_active(identifier))

    def create(self, data, user):
        self.require_player(user)
        team = {**data.model_dump(), "id": str(uuid4()), "owner_id": user["id"], "members": [user["id"]], "requests": [], "color": user["color"]}
        team["tag"] = team["tag"].upper()
        return self.view(self.repository.save(team))

    def owned(self, identifier, user):
        team = self.repository.require_active(identifier)
        if team["owner_id"] != user["id"]:
            raise HTTPException(403, "Solo el capitán puede gestionar este equipo.")
        return team

    def update(self, identifier, data, user):
        with lock:
            team = self.owned(identifier, user)
            if data.max_members < len(team["members"]):
                raise HTTPException(409, "No puedes reducir los cupos por debajo de la plantilla actual.")
            if any(tournament["game"] not in data.games for tournament in self.repository.active_tournaments(identifier)):
                raise HTTPException(409, "Conserva los juegos de tus torneos activos en las preferencias del equipo.")
            team.update(data.model_dump())
            team["tag"] = team["tag"].upper()
            return self.view(self.repository.save(team))

    def membership(self, identifier, user):
        team = self.repository.require_active(identifier)
        return {"member": user["id"] in team["members"], "requested": user["id"] in team.get("requests", [])}

    def request_join(self, identifier, user):
        self.require_player(user)
        with lock:
            team = self.repository.require_active(identifier)
            if user["id"] in team["members"]:
                raise HTTPException(409, "Ya formas parte de este equipo.")
            if not team["recruiting"] or len(team["members"]) >= team["max_members"]:
                raise HTTPException(409, "Este equipo no recibe solicitudes por ahora.")
            if user["id"] in team.get("requests", []):
                raise HTTPException(409, "Tu solicitud ya está pendiente.")
            team.setdefault("requests", []).append(user["id"])
            self.repository.save(team)
            return {"status": "pending"}

    @staticmethod
    def require_player(user):
        if user.get("account_type") == "sponsor":
            raise HTTPException(403, "Las plantillas de equipos están formadas por cuentas de jugadores.")

    def requests(self, identifier, user):
        team = self.owned(identifier, user)
        return [public_user(self.players.get(member)) for member in team.get("requests", []) if is_visible(self.repository.store, "users", self.players.get(member))]

    def decide(self, identifier, member_id, decision, user):
        with lock:
            team = self.owned(identifier, user)
            if member_id not in team.get("requests", []):
                raise HTTPException(404, "Esta solicitud ya no está disponible.")
            if decision == "accept":
                self.assert_roster_editable(identifier)
                if len(team["members"]) >= team["max_members"]:
                    raise HTTPException(409, "La plantilla del equipo está completa.")
                self.players.require_active(member_id)
                team["members"].append(member_id)
            team["requests"].remove(member_id)
            return self.view(self.repository.save(team))

    def assert_roster_editable(self, identifier):
        if self.repository.active_tournaments(identifier):
            raise HTTPException(409, "La plantilla está bloqueada mientras el equipo esté inscrito en un torneo abierto o en juego. Retira al equipo o termina el torneo antes de cambiarla.")

    def remove_member(self, identifier, member_id, user):
        with lock:
            team = self.repository.require_active(identifier)
            if user["id"] not in (team["owner_id"], member_id):
                raise HTTPException(403, "Solo el capitán o el propio jugador pueden retirar a un miembro.")
            if member_id == team["owner_id"]:
                raise HTTPException(409, "El capitán debe permanecer en su equipo.")
            self.assert_roster_editable(identifier)
            team["members"] = [member for member in team["members"] if member != member_id]
            return self.view(self.repository.save(team))
