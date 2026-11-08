from fastapi import APIRouter, Depends
from core.dependencies import get_store
from modules.auth.dependencies import current_user
from modules.players.repository.repository import PlayerRepository
from modules.players.schemas import Profile
from modules.players.services.service import PlayerService

router = APIRouter(prefix="/api/users", tags=["Jugadores"])


def get_service(store=Depends(get_store)):
    return PlayerService(PlayerRepository(store))


@router.get("")
def players(q: str = "", game: str = "", rank: str = "", available: bool = False, service=Depends(get_service)):
    return service.list(q, game, rank, available)


@router.put("/me")
def update_profile(data: Profile, user=Depends(current_user), service=Depends(get_service)):
    return service.update(data, user)


@router.get("/{identifier}")
def profile(identifier: str, service=Depends(get_service)):
    return service.profile(identifier)


@router.post("/{identifier}/connect")
def connect(identifier: str, user=Depends(current_user), service=Depends(get_service)):
    return service.connect(identifier, user)
