from typing import Literal
from fastapi import APIRouter, Depends
from core.dependencies import get_store
from modules.auth.dependencies import current_admin
from modules.admins.repository.repository import AdminRepository
from modules.admins.schemas import CaseDecision, NewAdmin, Unban
from modules.admins.services.service import AdminService

router = APIRouter(prefix="/api/admin", tags=["Administración"], dependencies=[Depends(current_admin)])


def get_service(store=Depends(get_store)):
    return AdminService(AdminRepository(store))


@router.get("/summary")
def summary(service=Depends(get_service)):
    return service.summary()


@router.get("/admins")
def admins(service=Depends(get_service)):
    return service.admins()


@router.post("/admins", status_code=201)
def create_admin(data: NewAdmin, actor=Depends(current_admin), service=Depends(get_service)):
    return service.create_admin(data, actor)


@router.get("/cases")
def cases(status: Literal["pending", "history"] = "pending", service=Depends(get_service)):
    return service.cases(status)


@router.get("/cases/{kind}/{identifier}")
def case(kind: str, identifier: str, service=Depends(get_service)):
    return service.case(kind, identifier)


@router.post("/cases/{kind}/{identifier}/decision")
def decide(kind: str, identifier: str, data: CaseDecision, actor=Depends(current_admin), service=Depends(get_service)):
    return service.decide(kind, identifier, data, actor)


@router.post("/cases/{kind}/{identifier}/unban")
def unban(kind: str, identifier: str, data: Unban, actor=Depends(current_admin), service=Depends(get_service)):
    return service.unban(kind, identifier, data, actor)
