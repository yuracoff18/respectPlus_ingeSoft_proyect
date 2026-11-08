from fastapi import APIRouter, Depends
from core.dependencies import get_store
from modules.auth.dependencies import current_user
from modules.players.repository.repository import PlayerRepository
from modules.teams.repository.repository import TeamRepository
from modules.teams.schemas import MembershipDecision, TeamInput
from modules.teams.services.service import TeamService

router = APIRouter(prefix="/api/teams", tags=["Equipos"])


def get_service(store=Depends(get_store)):
    return TeamService(TeamRepository(store), PlayerRepository(store))


@router.get("")
def teams(q: str = "", game: str = "", rank: str = "", recruiting: bool = False, service=Depends(get_service)):
    return service.list(q, game, rank, recruiting)


@router.post("", status_code=201)
def create(data: TeamInput, user=Depends(current_user), service=Depends(get_service)):
    return service.create(data, user)


@router.get("/{identifier}")
def profile(identifier: str, service=Depends(get_service)):
    return service.profile(identifier)


@router.put("/{identifier}")
def update(identifier: str, data: TeamInput, user=Depends(current_user), service=Depends(get_service)):
    return service.update(identifier, data, user)


@router.get("/{identifier}/membership")
def membership(identifier: str, user=Depends(current_user), service=Depends(get_service)):
    return service.membership(identifier, user)


@router.post("/{identifier}/requests", status_code=201)
def request_join(identifier: str, user=Depends(current_user), service=Depends(get_service)):
    return service.request_join(identifier, user)


@router.get("/{identifier}/requests")
def requests(identifier: str, user=Depends(current_user), service=Depends(get_service)):
    return service.requests(identifier, user)


@router.put("/{identifier}/requests/{member_id}")
def decide(identifier: str, member_id: str, data: MembershipDecision, user=Depends(current_user), service=Depends(get_service)):
    return service.decide(identifier, member_id, data.decision, user)


@router.delete("/{identifier}/members/{member_id}")
def remove_member(identifier: str, member_id: str, user=Depends(current_user), service=Depends(get_service)):
    return service.remove_member(identifier, member_id, user)
