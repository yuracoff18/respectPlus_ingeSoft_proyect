from fastapi import APIRouter, Depends
from core.dependencies import get_store
from modules.auth.dependencies import current_user
from modules.players.repository.repository import PlayerRepository
from modules.sponsors.repository.repository import SponsorRepository
from modules.sponsors.schemas import SponsorInput
from modules.sponsors.services.service import SponsorService
from modules.teams.repository.repository import TeamRepository

router = APIRouter(prefix="/api/sponsors", tags=["Sponsors"])


def get_service(store=Depends(get_store)):
    return SponsorService(SponsorRepository(store), TeamRepository(store), PlayerRepository(store))


@router.get("")
def sponsors(q: str = "", game: str = "", service=Depends(get_service)):
    return service.list(q, game)


@router.post("", status_code=201)
def create(data: SponsorInput, user=Depends(current_user), service=Depends(get_service)):
    return service.create(data, user)


@router.get("/{identifier}")
def profile(identifier: str, service=Depends(get_service)):
    return service.profile(identifier)


@router.put("/{identifier}")
def update(identifier: str, data: SponsorInput, user=Depends(current_user), service=Depends(get_service)):
    return service.update(identifier, data, user)
