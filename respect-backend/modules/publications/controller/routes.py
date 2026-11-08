from fastapi import APIRouter, Depends
from core.dependencies import get_store
from modules.auth.dependencies import current_user
from modules.players.repository.repository import PlayerRepository
from modules.publications.repository.repository import PublicationRepository
from modules.publications.schemas import Content, NewPost
from modules.publications.services.service import PublicationService

router = APIRouter(prefix="/api/posts", tags=["Publicaciones"])


def get_service(store=Depends(get_store)):
    return PublicationService(PublicationRepository(store), PlayerRepository(store))


@router.get("")
def posts(game: str = "", author: str = "", q: str = "", service=Depends(get_service)):
    return service.list(game, author, q)


@router.post("", status_code=201)
def create(data: NewPost, user=Depends(current_user), service=Depends(get_service)):
    return service.create(data, user)


@router.post("/{identifier}/like")
def like(identifier: str, user=Depends(current_user), service=Depends(get_service)):
    return service.like(identifier, user)


@router.post("/{identifier}/comments", status_code=201)
def comment(identifier: str, data: Content, user=Depends(current_user), service=Depends(get_service)):
    return service.comment(identifier, data, user)
