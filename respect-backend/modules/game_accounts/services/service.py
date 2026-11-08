import os
import time
from datetime import datetime, timezone
from fastapi import HTTPException
from modules.game_accounts.providers import riot, henrik, cs2, osirion
from modules.game_accounts.providers.http import IntegrationError
from modules.players.services.views import own_user
from store import lock

PROVIDERS = {
    "League of Legends": ("Riot Games", "RIOT_API_KEY", riot.fetch),
    "Valorant": ("HenrikDev", "HENRIK_API_KEY", henrik.fetch),
    "Counter-Strike 2": ("Steam / FACEIT", "STEAM_WEB_API_KEY", cs2.fetch),
    "Fortnite": ("Osirion", None, osirion.fetch),
    "Rocket League": (None, None, None),
    "EA Sports FC": (None, None, None),
}


class GameAccountService:
    def __init__(self, repository, players):
        self.repository = repository
        self.players = players

    def providers(self):
        result = [{"game": game, "provider": provider, "supported": fetcher is not None, "configured": fetcher is not None and (key is None or bool(os.getenv(key))), "message": "Requiere acceso de partner; no hay un conector de rangos público configurado." if fetcher is None else "Configura la clave del proveedor en el servidor." if key and not os.getenv(key) else "Consulta disponible."} for game, (provider, key, fetcher) in PROVIDERS.items()]
        for item in result:
            if item["game"] == "Counter-Strike 2":
                item["configured"] = bool(os.getenv("STEAM_WEB_API_KEY") or os.getenv("FACEIT_API_KEY"))
                item["message"] = "Steam permite consultar la cuenta, pero no su rango Premier. FACEIT ofrece su propio nivel competitivo con una clave independiente."
        return result

    def sync(self, data, user):
        if user.get("account_type") == "sponsor":
            raise HTTPException(403, "Las cuentas de juego y los rangos corresponden a perfiles de jugadores.")
        identifier = f"{user['id']}:{data.game}"
        with lock:
            current = self.players.require_active(user["id"])
            if data.game not in current.get("games", []):
                raise HTTPException(422, "Añade este juego a tus preferencias antes de sincronizarlo.")
            existing = self.repository.get(identifier)
            now = time.time()
            if existing and now - existing["last_attempt"] < 60:
                raise HTTPException(429, "Espera un minuto antes de volver a sincronizar este juego.")
            self.repository.save({"id": identifier, "user_id": user["id"], **data.model_dump(), "last_attempt": now})
        provider, _, fetcher = PROVIDERS[data.game]
        previous = current.get("game_profiles", {}).get(data.game, {})
        # Never carry a rank over to a different account or competitive queue.
        if not existing or any(existing.get(field) != getattr(data, field) for field in ("identifier", "region", "platform", "queue")):
            previous = {}
        try:
            if fetcher is None:
                raise IntegrationError("Este juego necesita acceso de partner a una API de rangos. No hay una fuente autorizada configurada.", "unsupported")
            snapshot = fetcher(data)
            snapshot["synced_at"] = datetime.now(timezone.utc).isoformat()
        except IntegrationError as error:
            snapshot = {**previous, "status": "stale" if previous.get("current_rank") else error.status, "note": str(error), "provider": provider}
        except (KeyError, TypeError, ValueError, AttributeError):
            snapshot = {**previous, "status": "stale" if previous.get("current_rank") else "error", "note": "El formato del proveedor cambió. No se actualizaron los rangos.", "provider": provider}
        snapshot.update({"game": data.game, "account_name": data.identifier, "region": data.region, "platform": data.platform})
        with lock:
            current = self.players.require_active(user["id"])
            current.setdefault("game_profiles", {})[data.game] = snapshot
            self.players.save(current)
            return own_user(current)

    def unlink(self, game, user):
        with lock:
            current = self.players.require_active(user["id"])
            current.setdefault("game_profiles", {}).pop(game, None)
            self.repository.store.delete("game_accounts", f"{user['id']}:{game}")
            return own_user(self.players.save(current))
