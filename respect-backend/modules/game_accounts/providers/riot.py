import os
import time
from collections import deque
from threading import Lock
from urllib.parse import quote
from .http import IntegrationError, get_json

REGIONS = {"la1": "americas", "la2": "americas", "na1": "americas", "br1": "americas", "euw1": "europe", "eun1": "europe", "tr1": "europe", "ru": "europe", "kr": "asia", "jp1": "asia", "oc1": "sea", "sg2": "sea", "tw2": "sea", "vn2": "sea"}
TIERS = {"IRON": "Hierro", "BRONZE": "Bronce", "SILVER": "Plata", "GOLD": "Oro", "PLATINUM": "Platino", "EMERALD": "Esmeralda", "DIAMOND": "Diamante", "MASTER": "Maestro", "GRANDMASTER": "Gran maestro", "CHALLENGER": "Retador"}
_request_times = deque()
_rate_lock = Lock()


def _request(client, url, headers):
    # Global per-process limit, including both Account-V1 and League-V4 calls.
    # API runs with one worker; never exceed the supplied key's 20 requests/s.
    while True:
        with _rate_lock:
            now = time.monotonic()
            while _request_times and now - _request_times[0] >= 120:
                _request_times.popleft()
            second_count = sum(now - stamp < 1 for stamp in _request_times)
            if second_count < 20 and len(_request_times) < 100:
                _request_times.append(now)
                break
            # Do not tie up the proxy waiting for the 2-minute development quota.
            if len(_request_times) >= 100:
                raise IntegrationError("Riot alcanzó el límite temporal de consultas. Inténtalo más tarde.")
        time.sleep(0.05)
    return client(url, headers)


def fetch(data, client=get_json):
    key = os.getenv("RIOT_API_KEY")
    if not key:
        raise IntegrationError("Falta configurar la clave de Riot Games en el servidor.", "not_configured")
    region = data.region.lower()
    if region not in REGIONS or data.queue not in ("solo", "flex") or "#" not in data.identifier:
        raise IntegrationError("Usa un Riot ID Nombre#TAG, una región válida y la cola Solo/Duo o Flex.")
    name, tag = data.identifier.rsplit("#", 1)
    if not name or not tag:
        raise IntegrationError("Escribe tu Riot ID como Nombre#TAG.")
    headers = {"X-Riot-Token": key}
    account = _request(client, f"https://{REGIONS[region]}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(name, safe='')}/{quote(tag, safe='')}", headers)
    entries = _request(client, f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/{quote(account['puuid'], safe='')}", headers)
    queue = "RANKED_SOLO_5x5" if data.queue == "solo" else "RANKED_FLEX_SR"
    entry = next((entry for entry in entries if entry["queueType"] == queue), None)
    rank = f"{TIERS.get(entry['tier'], entry['tier'])} {entry['rank']}" if entry else "Sin clasificación"
    return {"current_rank": rank, "peak_rank": None, "rank_points": entry.get("leaguePoints") if entry else None, "queue": "Solo/Duo" if data.queue == "solo" else "Flex", "provider": "Riot Games", "source_url": "https://developer.riotgames.com/docs/lol", "note": "La API devuelve el rango actual de esta cola; no ofrece su pico histórico.", "status": "synced" if entry else "unranked"}
