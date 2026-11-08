from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException
from core.visibility import is_visible
from modules.reports.repository.repository import TARGET_COLLECTIONS
from store import lock


class ReportService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, data, user):
        with lock:
            target = self.repository.target(data.target_type, data.target_id)
            if not is_visible(self.repository.store, TARGET_COLLECTIONS[data.target_type], target) or target.get("role") == "admin" or (data.target_type == "player" and target.get("account_type") == "sponsor"):
                raise HTTPException(404, "Este perfil no está disponible.")
            owner_id = target["id"] if data.target_type == "player" else target["owner_id"]
            if user["id"] == owner_id:
                raise HTTPException(400, "No puedes reportar tu propio perfil o entidad.")
            if any(report["reporter_id"] == user["id"] for report in self.repository.pending(data.target_type, data.target_id)):
                raise HTTPException(409, "Ya tienes un reporte pendiente sobre este perfil.")
            publication = None
            if data.publication_id:
                post = self.repository.store.get("posts", data.publication_id)
                if not post or post.get("hidden"):
                    raise HTTPException(404, "Esta publicación no está disponible.")
                publisher_type = post.get("publisher_type", "player")
                publisher_id = post.get("publisher_id") or post["author_id"]
                if (publisher_type, publisher_id) != (data.target_type, data.target_id):
                    raise HTTPException(422, "La publicación no pertenece al perfil reportado.")
                publication = {"id": post["id"], "content": post["content"], "game": post["game"], "created_at": post["created_at"], "author_id": post["author_id"], "publisher_name": target["name"]}
            report = {**data.model_dump(), "id": str(uuid4()), "reporter_id": user["id"], "status": "pending", "created_at": datetime.now(timezone.utc).isoformat(), "publication": publication, "target_name": target["name"]}
            self.repository.save(report)
            return {"id": report["id"], "status": "pending", "message": "Reporte enviado para revisión."}
