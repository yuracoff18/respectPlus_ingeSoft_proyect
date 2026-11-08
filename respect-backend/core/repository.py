from fastapi import HTTPException
from store import Store
from core.visibility import is_visible


class DocumentRepository:
    """Persistence boundary shared by domain-specific repositories."""
    collection = ""

    def __init__(self, store: Store):
        self.store = store

    def all(self):
        return self.store.all(self.collection)

    def get(self, identifier):
        return self.store.get(self.collection, identifier)

    def require(self, identifier):
        document = self.get(identifier)
        if document is None:
            raise HTTPException(404, "No encontramos lo que buscas.")
        return document

    def save(self, document):
        return self.store.put(self.collection, document)

    def active(self):
        return [document for document in self.all() if is_visible(self.store, self.collection, document)]

    def require_active(self, identifier):
        document = self.require(identifier)
        if not is_visible(self.store, self.collection, document):
            raise HTTPException(404, "Este perfil no está disponible.")
        return document
