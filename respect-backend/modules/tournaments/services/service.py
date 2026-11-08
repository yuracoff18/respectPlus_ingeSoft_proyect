from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException
from modules.tournaments.services.bracket import advance, generate
from modules.players.services.views import public_user
from store import lock


class TournamentService:
    def __init__(self, repository, teams, players):
        self.repository = repository
        self.teams = teams
        self.players = players

    def view(self, tournament):
        result = {"mode": "solo", "team_size": 1, "rosters": {}, **tournament}
        owner = self.players.get(tournament["owner_id"])
        result["owner_href"] = public_user(owner)["profile_href"] if owner else None
        if owner:
            result["owner_name"] = owner["name"]
        result["participant_details"] = []
        for identifier in result["participants"]:
            team_mode = result["mode"] == "team"
            entity = self.teams.get(identifier) if team_mode else self.players.get(identifier)
            result["participant_details"].append({"id": identifier, "name": entity["name"] if entity and not entity.get("banned") else "Participante no disponible", "type": "team" if team_mode else "player", "href": (f"/equipos/{identifier}" if team_mode else f"/jugadores/{entity['username']}") if entity and not entity.get("banned") else None})
        return result

    def list(self, game="", mode="", q=""):
        tournaments = [tournament for tournament in self.repository.active() if (not game or tournament["game"] == game) and (not mode or tournament.get("mode", "solo") == mode) and (not q or q.casefold() in tournament["title"].casefold())]
        return [self.view(tournament) for tournament in sorted(tournaments, key=lambda value: value["starts_at"])]

    def profile(self, identifier):
        return self.view(self.repository.require_active(identifier))

    def create(self, data, user):
        tournament = {**data.model_dump(mode="json"), "id": str(uuid4()), "owner_id": user["id"], "owner_name": user["name"], "participants": [], "rosters": {}, "status": "open", "rounds": []}
        return self.view(self.repository.save(tournament))

    def entry(self, tournament, data, user):
        if user.get("account_type") == "sponsor":
            raise HTTPException(403, "Las empresas pueden organizar torneos; las inscripciones corresponden a jugadores o equipos.")
        if tournament.get("mode", "solo") == "solo":
            if data.team_id:
                raise HTTPException(422, "Este torneo es individual.")
            return user["id"], None
        if not data.team_id:
            raise HTTPException(422, "Selecciona el equipo que vas a inscribir.")
        team = self.teams.require_active(data.team_id)
        if team["owner_id"] != user["id"]:
            raise HTTPException(403, "Solo el capitán puede inscribir o retirar a su equipo.")
        return team["id"], team

    def validate_roster(self, tournament, team, roster):
        if tournament["game"] not in team["games"]:
            raise HTTPException(422, "El equipo debe tener este juego entre sus preferencias.")
        if not roster or len(roster) != tournament["team_size"] or len(set(roster)) != len(roster):
            raise HTTPException(422, f"Selecciona exactamente {tournament['team_size']} jugadores distintos de la plantilla.")
        if any(identifier not in team["members"] for identifier in roster):
            raise HTTPException(422, "Todos los inscritos deben formar parte del equipo.")
        for identifier in roster:
            self.players.require_active(identifier)

    def join(self, identifier, data, user):
        with lock:
            tournament = self.repository.require_active(identifier)
            self.assert_open(tournament)
            entry_id, team = self.entry(tournament, data, user)
            if entry_id in tournament["participants"]:
                raise HTTPException(409, "Ya estás inscrito en este torneo.")
            if len(tournament["participants"]) >= tournament["capacity"]:
                raise HTTPException(409, "Este torneo ya está completo.")
            if datetime.fromisoformat(tournament["starts_at"]) <= datetime.now(timezone.utc):
                raise HTTPException(409, "La fecha de inscripción ya pasó.")
            if team:
                self.validate_roster(tournament, team, data.roster)
                occupied = {member for roster in tournament.get("rosters", {}).values() for member in roster}
                if occupied.intersection(data.roster):
                    raise HTTPException(409, "Un jugador ya está inscrito con otro equipo en este torneo.")
                tournament.setdefault("rosters", {})[entry_id] = data.roster
            tournament["participants"].append(entry_id)
            return self.view(self.repository.save(tournament))

    def leave(self, identifier, data, user):
        with lock:
            tournament = self.repository.require_active(identifier)
            self.assert_open(tournament)
            entry_id, _ = self.entry(tournament, data, user)
            tournament["participants"] = [value for value in tournament["participants"] if value != entry_id]
            tournament.get("rosters", {}).pop(entry_id, None)
            return self.view(self.repository.save(tournament))

    @staticmethod
    def assert_open(tournament):
        if tournament["status"] != "open":
            raise HTTPException(409, "Las inscripciones de este torneo están cerradas.")

    def owned(self, identifier, user):
        tournament = self.repository.require_active(identifier)
        if tournament["owner_id"] != user["id"]:
            raise HTTPException(403, "Solo el organizador puede gestionar el torneo.")
        return tournament

    def start(self, identifier, user):
        with lock:
            tournament = self.owned(identifier, user)
            self.assert_open(tournament)
            if len(tournament["participants"]) < 2:
                raise HTTPException(409, "Necesitas al menos 2 participantes para iniciar el torneo.")
            if tournament.get("mode", "solo") == "team":
                for identifier in tournament["participants"]:
                    self.validate_roster(tournament, self.teams.require_active(identifier), tournament["rosters"].get(identifier))
            tournament["rounds"] = generate(tournament["participants"])
            tournament["status"] = "live"
            advance(tournament)
            return self.view(self.repository.save(tournament))

    def report_score(self, identifier, match_id, score, user):
        with lock:
            tournament = self.owned(identifier, user)
            if tournament["status"] != "live":
                raise HTTPException(409, "El torneo no está en juego.")
            match = next((match for round_ in tournament["rounds"] for match in round_ if match["id"] == match_id), None)
            if not match or not match["a"] or not match["b"] or match["winner"]:
                raise HTTPException(409, "Este enfrentamiento aún no está disponible o ya fue cerrado.")
            if score.score_a == score.score_b:
                raise HTTPException(422, "En eliminación directa no puede haber empate.")
            match.update(score.model_dump())
            match["winner"] = match["a"] if score.score_a > score.score_b else match["b"]
            advance(tournament)
            return self.view(self.repository.save(tournament))
