"""Document storage: MongoDB in Compose, durable SQLite for local development."""
import json
import os
import sqlite3
from pathlib import Path
from threading import RLock
from urllib.parse import quote_plus

lock = RLock()


class Store:
    def __init__(self):
        uri = os.getenv("MONGO_URI")
        if not uri and os.getenv("MONGO_HOST"):
            user = quote_plus(os.environ["MONGO_USER"])
            password = quote_plus(os.environ["MONGO_PASSWORD"])
            database = os.getenv("MONGO_DATABASE", "respectdb")
            uri = f"mongodb://{user}:{password}@{os.environ['MONGO_HOST']}:27017/{database}?authSource={database}"
        self.mongo = None
        self.sql = None
        if uri:
            from pymongo import MongoClient
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
            self.mongo = self.client[os.getenv("MONGO_DATABASE", "respectdb")]
            self.mongo.users.create_index("email", unique=True, partialFilterExpression={"email": {"$type": "string"}})
            self.mongo.users.create_index("username", unique=True, partialFilterExpression={"username": {"$type": "string"}})
        else:
            path = Path(os.getenv("SQLITE_PATH", "data/respect.db"))
            path.parent.mkdir(parents=True, exist_ok=True)
            self.sql = sqlite3.connect(str(path), check_same_thread=False)
            self.sql.execute("PRAGMA journal_mode=WAL")
            self.sql.execute("CREATE TABLE IF NOT EXISTS documents (collection TEXT, id TEXT, data TEXT, PRIMARY KEY(collection, id))")
            self.sql.commit()

    def all(self, collection):
        with lock:
            if self.mongo is not None:
                return [{k: v for k, v in doc.items() if k != "_id"} for doc in self.mongo[collection].find({"id": {"$exists": True}})]
            return [json.loads(row[0]) for row in self.sql.execute("SELECT data FROM documents WHERE collection = ?", (collection,)).fetchall()]

    def get(self, collection, identifier):
        with lock:
            if self.mongo is not None:
                return self.mongo[collection].find_one({"id": identifier}, {"_id": 0})
            row = self.sql.execute("SELECT data FROM documents WHERE collection = ? AND id = ?", (collection, identifier)).fetchone()
            return json.loads(row[0]) if row else None

    def put(self, collection, document):
        with lock:
            if self.mongo is not None:
                self.mongo[collection].replace_one({"id": document["id"]}, document, upsert=True)
            else:
                self.sql.execute("INSERT OR REPLACE INTO documents VALUES (?, ?, ?)", (collection, document["id"], json.dumps(document)))
                self.sql.commit()
        return document

    def delete(self, collection, identifier):
        with lock:
            if self.mongo is not None:
                self.mongo[collection].delete_one({"id": identifier})
            else:
                self.sql.execute("DELETE FROM documents WHERE collection = ? AND id = ?", (collection, identifier))
                self.sql.commit()

    def healthy(self):
        if self.mongo is not None:
            self.client.admin.command("ping")
        else:
            with lock:
                self.sql.execute("SELECT 1")

    def clear_collections(self, collections):
        counts = {}
        with lock:
            for collection in collections:
                if self.mongo is not None:
                    counts[collection] = self.mongo[collection].count_documents({})
                    self.mongo[collection].delete_many({})
                else:
                    counts[collection] = self.sql.execute("SELECT COUNT(*) FROM documents WHERE collection = ?", (collection,)).fetchone()[0]
                    self.sql.execute("DELETE FROM documents WHERE collection = ?", (collection,))
            if self.sql:
                self.sql.commit()
        return counts

    def close(self):
        if self.mongo is not None:
            self.client.close()
        elif self.sql:
            self.sql.close()
