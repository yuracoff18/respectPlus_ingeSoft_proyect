from fastapi import APIRouter, Depends
from core.dependencies import get_store
from modules.auth.dependencies import current_user
from modules.players.repository.repository import PlayerRepository
from modules.teams.repository.repository import TeamRepository
from modules.tournaments.repository.repository import TournamentRepository
from modules.tournaments.schemas import JoinRequest, NewTournament, Score
from modules.tournaments.services.service import TournamentService

router = APIRouter(prefix="/api/tournaments", tags=["Torneos"])


def get_service(store=Depends(get_store)):
    return TournamentService(TournamentRepository(store), TeamRepository(store), PlayerRepository(store))


@router.get("")
def tournaments(game: str = "", mode: str = "", q: str = "", service=Depends(get_service)):
    return service.list(game, mode, q)


@router.post("", status_code=201)
def create(data: NewTournament, user=Depends(current_user), service=Depends(get_service)):
    return service.create(data, user)


@router.get("/{identifier}")
def tournament(identifier: str, service=Depends(get_service)):
    return service.profile(identifier)


@router.post("/{identifier}/join")
def join(identifier: str, data: JoinRequest | None = None, user=Depends(current_user), service=Depends(get_service)):
    return service.join(identifier, data or JoinRequest(), user)


@router.delete("/{identifier}/join")
def leave(identifier: str, data: JoinRequest | None = None, user=Depends(current_user), service=Depends(get_service)):
    return service.leave(identifier, data or JoinRequest(), user)


@router.post("/{identifier}/start")
def start(identifier: str, user=Depends(current_user), service=Depends(get_service)):
    return service.start(identifier, user)


@router.put("/{identifier}/matches/{match_id}")
def report_score(identifier: str, match_id: str, data: Score, user=Depends(current_user), service=Depends(get_service)):
    return service.report_score(identifier, match_id, data, user)
