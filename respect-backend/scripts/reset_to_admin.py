"""Explicit maintenance command for the user-requested clean application state."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.bootstrap import bootstrap_admin, validate_admin_password
from store import Store, lock

COLLECTIONS = ("users", "sessions", "posts", "publications", "players", "teams", "sponsors", "tournaments", "reports", "moderation_actions", "game_accounts", "settings", "admins", "request", "requests", "tournamentsRequest", "playersApisTokens", "games")


def reset_to_admin(store):
    # Validate the replacement account before deleting any application data.
    validate_admin_password(os.environ.get("BOOTSTRAP_ADMIN_PASSWORD", ""))
    username = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin")
    import re
    if not re.fullmatch(r"[a-zA-Z0-9_]{3,24}", username):
        raise ValueError("Usuario administrador inválido")
    with lock:
        counts = store.clear_collections(COLLECTIONS)
        admin = bootstrap_admin(store)
        return {"removed": counts, "remaining_users": len(store.all("users")), "admin_username": admin["username"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply the explicitly requested application-data reset")
    args = parser.parse_args()
    if not args.apply:
        parser.error("Este comando elimina los datos de la aplicación; requiere --apply.")
    store = Store()
    try:
        if store.mongo is not None and store.mongo.name != "respectdb":
            raise ValueError("Solo se permite limpiar la base de este proyecto: respectdb")
        if store.mongo is None:
            database_path = Path(os.getenv("SQLITE_PATH", "data/respect.db")).resolve()
            if not database_path.is_relative_to(ROOT):
                raise ValueError("La base SQLite debe estar dentro de respect-backend")
        print(json.dumps(reset_to_admin(store)))
    finally:
        store.close()
