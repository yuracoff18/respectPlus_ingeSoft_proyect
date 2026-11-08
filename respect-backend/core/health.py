from fastapi import APIRouter, Depends
from core.dependencies import get_store

router = APIRouter(tags=["Estado"])


@router.get("/api/health")
def health(store=Depends(get_store)):
    store.healthy()
    return {"status": "ok", "database": "mongodb" if store.mongo is not None else "sqlite"}
