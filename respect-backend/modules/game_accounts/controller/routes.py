from fastapi import APIRouter, Depends
from core.dependencies import get_store
from modules.auth.dependencies import current_user
from modules.game_accounts.repository.repository import GameAccountRepository
from modules.game_accounts.schemas import SyncAccount
from modules.game_accounts.services.service import GameAccountService
from modules.players.repository.repository import PlayerRepository

router = APIRouter(prefix="/api/game-accounts", tags=["Cuentas y rangos"])


def get_service(store=Depends(get_store)):
    return GameAccountService(GameAccountRepository(store), PlayerRepository(store))


@router.get("/providers")
def providers(service=Depends(get_service)):
    return service.providers()


@router.post("/sync")
def sync(data: SyncAccount, user=Depends(current_user), service=Depends(get_service)):
    return service.sync(data, user)


@router.delete("/{game}")
def unlink(game: str, user=Depends(current_user), service=Depends(get_service)):
    return service.unlink(game, user)
