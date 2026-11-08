from core.repository import DocumentRepository


class TeamRepository(DocumentRepository):
    collection = "teams"

    def active_tournaments(self, identifier):
        return [tournament for tournament in self.store.all("tournaments") if tournament.get("mode", "solo") == "team" and identifier in tournament["participants"] and tournament["status"] in ("open", "live")]
