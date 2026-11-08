from core.repository import DocumentRepository

TARGET_COLLECTIONS = {"player": "users", "team": "teams", "sponsor": "sponsors"}


class ReportRepository(DocumentRepository):
    collection = "reports"

    def target(self, target_type, identifier):
        return self.store.get(TARGET_COLLECTIONS[target_type], identifier)

    def pending(self, target_type, identifier):
        return [report for report in self.all() if report["target_type"] == target_type and report["target_id"] == identifier and report["status"] == "pending"]
