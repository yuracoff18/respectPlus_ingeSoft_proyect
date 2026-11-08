from core.repository import DocumentRepository
from modules.reports.repository.repository import TARGET_COLLECTIONS


class AdminRepository(DocumentRepository):
    collection = "users"

    def reports(self):
        return self.store.all("reports")

    def target(self, kind, identifier):
        return self.store.get(TARGET_COLLECTIONS[kind], identifier)

    def decisions(self):
        return self.store.all("moderation_actions")

    def revoke_sessions(self, user_id):
        for session in self.store.all("sessions"):
            if session["user_id"] == user_id:
                self.store.delete("sessions", session["id"])
