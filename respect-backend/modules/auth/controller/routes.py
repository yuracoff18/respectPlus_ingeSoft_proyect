from fastapi import APIRouter, Depends, Request, Response
from core.security import rate_limit
from modules.auth.dependencies import current_user, get_auth_service
from modules.auth.schemas import Login, Register
from modules.players.services.views import own_user

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/register", status_code=201)
def register(data: Register, request: Request, response: Response, service=Depends(get_auth_service)):
    rate_limit(request)
    return service.register(data, response)


@router.post("/login")
def login(data: Login, request: Request, response: Response, service=Depends(get_auth_service)):
    rate_limit(request)
    return service.login(data, response)


@router.get("/me")
def me(user=Depends(current_user)):
    return own_user(user)


@router.post("/logout")
def logout(request: Request, response: Response, service=Depends(get_auth_service)):
    return service.logout(request.cookies.get("respect_session", ""), response)
