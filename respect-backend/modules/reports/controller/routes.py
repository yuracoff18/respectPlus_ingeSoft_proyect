from fastapi import APIRouter, Depends
from core.dependencies import get_store
from modules.auth.dependencies import current_user
from modules.reports.repository.repository import ReportRepository
from modules.reports.schemas import NewReport
from modules.reports.services.service import ReportService

router = APIRouter(prefix="/api/reports", tags=["Reportes"])


@router.post("", status_code=201)
def create(data: NewReport, user=Depends(current_user), store=Depends(get_store)):
    return ReportService(ReportRepository(store)).create(data, user)
