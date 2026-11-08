from collections import defaultdict
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException
from core.security import password_hash
from modules.players.services.views import public_user
from modules.reports.repository.repository import TARGET_COLLECTIONS
from store import lock


class AdminService:
    def __init__(self, repository):
        self.repository = repository

    def admins(self):
        return [{"id": user["id"], "username": user["username"], "name": user["name"], "role": "admin", "created_at": user.get("created_at")} for user in self.repository.all() if user.get("role") == "admin"]

    def create_admin(self, data, actor):
        with lock:
            if any(user["username"].casefold() == data.username.casefold() or user.get("email") == data.email for user in self.repository.all()):
                raise HTTPException(409, "El correo o el usuario ya está registrado.")
            now = datetime.now(timezone.utc).isoformat()
            user = {"id": str(uuid4()), "username": data.username.lower(), "name": data.name, "email": data.email, "password_hash": password_hash(data.password), "role": "admin", "banned": False, "games": [], "game_profiles": {}, "game": "", "country": "Colombia", "available": False, "headline": "Moderación de la comunidad", "bio": "", "connections": [], "color": "#c1515d", "created_at": now}
            self.repository.save(user)
            self.repository.store.put("moderation_actions", {"id": str(uuid4()), "action": "create_admin", "actor_id": actor["id"], "target_type": "player", "target_id": user["id"], "created_at": now, "reason": "Creación de administrador autorizado", "report_ids": []})
            return {"id": user["id"], "name": user["name"], "username": user["username"], "role": "admin"}

    def summary(self):
        store = self.repository.store
        return {"players": sum(user.get("role", "player") == "player" and user.get("account_type", "player") == "player" for user in self.repository.all()), "teams": len(store.all("teams")), "sponsors": len(store.all("sponsors")), "admins": len(self.admins()), "pending_cases": len(self.cases()), "threshold": 5}

    def case(self, kind, identifier):
        if kind not in TARGET_COLLECTIONS:
            raise HTTPException(422, "Tipo de perfil no válido.")
        target = self.repository.target(kind, identifier)
        if not target or target.get("role") == "admin" or (kind == "player" and target.get("account_type") == "sponsor"):
            raise HTTPException(404, "Este perfil no está disponible para moderación.")
        reports = []
        for report in self.repository.reports():
            if (report["target_type"], report["target_id"]) != (kind, identifier):
                continue
            reporter = self.repository.get(report["reporter_id"])
            reports.append({**report, "reporter_name": reporter["name"] if reporter else "Cuenta eliminada"})
        history = [action for action in self.repository.decisions() if action.get("target_type") == kind and action.get("target_id") == identifier]
        return {"target_type": kind, "target_id": identifier, "name": target["name"], "banned": bool(target.get("banned")), "pending_count": sum(report["status"] == "pending" for report in reports), "total_count": len(reports), "reports": sorted(reports, key=lambda report: report["created_at"], reverse=True), "history": sorted(history, key=lambda action: action["created_at"], reverse=True)}

    def cases(self, status="pending"):
        groups = defaultdict(int)
        for report in self.repository.reports():
            if status != "pending" or report["status"] == "pending":
                groups[(report["target_type"], report["target_id"])] += 1
        cases = [self.case(kind, identifier) for (kind, identifier), count in groups.items() if count > 5]
        return sorted(cases, key=lambda case: case["pending_count"], reverse=True)

    def decide(self, kind, identifier, data, actor):
        with lock:
            case = self.case(kind, identifier)
            if case["pending_count"] <= 5:
                raise HTTPException(409, "El caso necesita más de 5 reportes pendientes para entrar en revisión.")
            pending = {report["id"] for report in case["reports"] if report["status"] == "pending"}
            selected = set(data.report_ids)
            if not selected or not selected.issubset(pending):
                raise HTTPException(409, "El caso cambió. Actualiza antes de decidir.")
            now = datetime.now(timezone.utc).isoformat()
            if data.action == "ban":
                target = self.repository.target(kind, identifier)
                target.update({"banned": True, "banned_at": now, "banned_by": actor["id"], "moderation_note": data.reason})
                self.repository.store.put(TARGET_COLLECTIONS[kind], target)
                if kind == "player":
                    self.repository.revoke_sessions(identifier)
                elif kind == "sponsor":
                    owner = self.repository.get(target["owner_id"])
                    if owner and owner.get("account_type") == "sponsor" and owner.get("sponsor_id") == identifier:
                        self.repository.revoke_sessions(owner["id"])
            for report in case["reports"]:
                if report["id"] not in selected:
                    continue
                record = self.repository.store.get("reports", report["id"])
                record.update({"status": "accepted" if data.action == "ban" else "dismissed", "reviewed_at": now, "reviewed_by": actor["id"]})
                self.repository.store.put("reports", record)
            self.repository.store.put("moderation_actions", {"id": str(uuid4()), "action": data.action, "actor_id": actor["id"], "target_type": kind, "target_id": identifier, "reason": data.reason, "report_ids": list(selected), "created_at": now})
            return self.case(kind, identifier)

    def unban(self, kind, identifier, data, actor):
        with lock:
            self.case(kind, identifier)
            target = self.repository.target(kind, identifier)
            if not target.get("banned"):
                raise HTTPException(409, "Este perfil no está suspendido.")
            target["banned"] = False
            self.repository.store.put(TARGET_COLLECTIONS[kind], target)
            self.repository.store.put("moderation_actions", {"id": str(uuid4()), "action": "unban", "actor_id": actor["id"], "target_type": kind, "target_id": identifier, "reason": data.reason, "report_ids": [], "created_at": datetime.now(timezone.utc).isoformat()})
            return self.case(kind, identifier)
