from core.repository import DocumentRepository


class PlayerRepository(DocumentRepository):
    collection = "users"

    def find_profile(self, identifier):
        direct = self.get(identifier)
        return direct or next((user for user in self.all() if user["username"].lower() == identifier.lower()), None)
