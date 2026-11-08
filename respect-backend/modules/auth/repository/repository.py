from core.repository import DocumentRepository


class AuthRepository(DocumentRepository):
    collection = "users"

    def by_identifier(self, identifier):
        return next((user for user in self.all() if identifier in (user.get("email", "").lower(), user["username"].lower())), None)

    def identity_taken(self, email, username):
        return any(user.get("email") == email or user["username"].lower() == username.lower() for user in self.all())

    def create_account(self, user, sponsor=None):
        self.save(user)
        try:
            if sponsor:
                self.store.put("sponsors", sponsor)
        except Exception:
            # Do not leave a login without its organization if creation fails.
            self.store.delete("sponsors", sponsor["id"])
            self.store.delete("users", user["id"])
            raise
        return user

    def session(self, identifier):
        return self.store.get("sessions", identifier)

    def save_session(self, session):
        return self.store.put("sessions", session)

    def delete_session(self, identifier):
        self.store.delete("sessions", identifier)

    def delete_expired(self, now):
        for session in self.store.all("sessions"):
            if session["expires_at"] < now:
                self.delete_session(session["id"])
