import os
import time
from collections import deque
from threading import Lock
from urllib.parse import quote
from .http import IntegrationError, get_json

_request_times = deque()
_rate_lock = Lock()


def _request(client, url, headers):
    # Shared across all players in the single backend worker. Count failures too.
    with _rate_lock:
        now = time.monotonic()
        while _request_times and now - _request_times[0] >= 60:
            _request_times.popleft()
        if len(_request_times) >= 30:
            raise IntegrationError("Valorant alcanzó el límite de 30 consultas por minuto. Inténtalo más tarde.")
        _request_times.append(now)
    return client(url, headers)


def fetch(data, client=get_json):
    key = os.getenv("HENRIK_API_KEY")
    if not key:
        raise IntegrationError("Falta configurar la clave de HenrikDev para Valorant.", "not_configured")
    if data.region not in ("na", "eu", "ap", "kr", "br", "latam") or data.platform not in ("pc", "console") or "#" not in data.identifier:
        raise IntegrationError("Usa un Riot ID Nombre#TAG y una región/plataforma de Valorant válida.")
    name, tag = data.identifier.rsplit("#", 1)
    if not name or not tag:
        raise IntegrationError("Escribe tu Riot ID como Nombre#TAG.")
    response = _request(client, f"https://api.henrikdev.xyz/valorant/v3/mmr/{data.region}/{data.platform}/{quote(name, safe='')}/{quote(tag, safe='')}", {"Authorization": key})
    body = response["data"]
    current = body.get("current", {})
    peak = body.get("peak") or {}
    return {"current_rank": current.get("tier", {}).get("name") or "Sin clasificación", "peak_rank": (peak.get("tier") or {}).get("name"), "peak_scope": "Histórico del proveedor", "rank_points": current.get("rr"), "queue": "Competitivo", "provider": "HenrikDev", "source_url": "https://docs.henrikdev.xyz/valorant/api-reference/mmr", "note": "Datos de un proveedor independiente de Riot Games.", "status": "synced" if current.get("tier") else "unranked"}
