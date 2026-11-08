from fastapi import Depends, HTTPException, Request
from core.dependencies import get_store
from modules.auth.repository.repository import AuthRepository
from modules.auth.services.service import AuthService


def get_auth_service(store=Depends(get_store)):
    return AuthService(AuthRepository(store))


def current_user(request: Request, service=Depends(get_auth_service)):
    return service.current(request.cookies.get("respect_session", ""))


def current_admin(user=Depends(current_user)):
    if user.get("role") != "admin":
        raise HTTPException(403, "Solo los administradores pueden acceder a este apartado.")
    return user
