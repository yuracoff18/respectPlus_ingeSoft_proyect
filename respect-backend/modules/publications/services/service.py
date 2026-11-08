from datetime import datetime, timezone
from uuid import uuid4
from modules.players.services.views import public_user
from store import lock
from fastapi import HTTPException
from core.visibility import is_visible
from modules.reports.repository.repository import TARGET_COLLECTIONS


class PublicationService:
    def __init__(self, repository, players):
        self.repository = repository
        self.players = players

    def view(self, post):
        kind = post.get("publisher_type", "player")
        identifier = post.get("publisher_id") or post["author_id"]
        publisher = self.repository.store.get(TARGET_COLLECTIONS[kind], identifier)
        href = f"/jugadores/{publisher['username']}" if kind == "player" else f"/{'equipos' if kind == 'team' else 'sponsors'}/{identifier}"
        comments = [comment for comment in post["comments"] if is_visible(self.repository.store, "users", self.players.get(comment["author_id"]))]
        return {**{key: value for key, value in post.items() if key != "author_id"}, "publisher": {"id": identifier, "type": kind, "name": publisher["name"], "color": publisher["color"], "href": href}, "author": public_user(self.players.require(post["author_id"])), "comments": [{**{key: value for key, value in comment.items() if key != "author_id"}, "author": public_user(self.players.require(comment["author_id"]))} for comment in comments]}

    def visible(self, post):
        kind = post.get("publisher_type", "player")
        publisher = self.repository.store.get(TARGET_COLLECTIONS[kind], post.get("publisher_id") or post["author_id"])
        return not post.get("hidden") and is_visible(self.repository.store, "users", self.players.get(post["author_id"])) and is_visible(self.repository.store, TARGET_COLLECTIONS[kind], publisher)

    def require_visible(self, identifier):
        post = self.repository.require(identifier)
        if not self.visible(post):
            raise HTTPException(404, "Esta publicación no está disponible.")
        return post

    def list(self, game="", author="", q=""):
        posts = [post for post in self.repository.all() if self.visible(post) and (not game or post["game"] == game) and (not author or post["author_id"] == author) and (not q or q.casefold() in post["content"].casefold())]
        return [self.view(post) for post in sorted(posts, key=lambda value: value["created_at"], reverse=True)]

    def create(self, data, user):
        if user.get("account_type") == "sponsor":
            if data.publisher_type not in ("player", "sponsor") or (data.publisher_id and data.publisher_id != user["sponsor_id"]):
                raise HTTPException(403, "Una cuenta de empresa solo puede publicar como su propia organización.")
            data.publisher_type = "sponsor"
            data.publisher_id = user["sponsor_id"]
        if data.publisher_type == "player":
            data.publisher_id = user["id"]
        else:
            entity = self.repository.store.get(TARGET_COLLECTIONS[data.publisher_type], data.publisher_id)
            if not is_visible(self.repository.store, TARGET_COLLECTIONS[data.publisher_type], entity) or entity["owner_id"] != user["id"]:
                raise HTTPException(403, "Solo puedes publicar como un equipo o sponsor que administras.")
        post = {"id": str(uuid4()), "author_id": user["id"], **data.model_dump(), "created_at": datetime.now(timezone.utc).isoformat(), "likes": [], "comments": []}
        return self.view(self.repository.save(post))

    def like(self, identifier, user):
        with lock:
            post = self.require_visible(identifier)
            post["likes"] = [uid for uid in post["likes"] if uid != user["id"]] if user["id"] in post["likes"] else [*post["likes"], user["id"]]
            return self.view(self.repository.save(post))

    def comment(self, identifier, data, user):
        with lock:
            post = self.require_visible(identifier)
            post["comments"].append({"id": str(uuid4()), "author_id": user["id"], "content": data.content, "created_at": datetime.now(timezone.utc).isoformat()})
            return self.view(self.repository.save(post))
