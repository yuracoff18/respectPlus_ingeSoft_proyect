import re
from datetime import datetime, timezone
from urllib.parse import urlencode
from .http import IntegrationError, get_json

BASE = "https://dev.fnapi.osirion.gg"


def fetch(data, client=get_json):
    if data.queue not in ("ranked-br", "ranked-zb"):
        raise IntegrationError("Selecciona Battle Royale o Cero construcción para Fortnite.")
    identifier = data.identifier
    if re.fullmatch(r"[a-f0-9]{32}", identifier):
        account_id = identifier
    else:
        lookup = client(BASE + "/v1/accounts/lookup-by-display-name?" + urlencode({"displayName": identifier, "platform": "epic"}))
        matches = lookup.get("accounts", [])
        exact = [account for account in matches if (account.get("accountDetails", {}).get("epic") or "").casefold() == identifier.casefold()]
        if len(exact) == 1:
            account_id = exact[0]["accountId"]
        elif len(matches) == 1:
            account_id = matches[0]["accountId"]
        else:
            raise IntegrationError("No encontramos una cuenta única. Usa tu Epic Account ID.")
    progress = client(BASE + "/v1/ranked/account-ranks?" + urlencode({"accountId": account_id, "lang": "es"}))
    modes = client(BASE + "/v1/ranked/modes?lang=es")
    if not progress.get("success", True) or not modes.get("success", True):
        raise IntegrationError("El proveedor de Fortnite no pudo completar la consulta.")
    now = datetime.now(timezone.utc)
    current_tracks = set()
    for mode in modes.get("modes", []):
        if mode["rankingType"] != data.queue:
            continue
        for season in mode["seasons"]:
            start = datetime.fromisoformat(season["seasonStart"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(season["seasonEnd"].replace("Z", "+00:00"))
            if start <= now < end:
                current_tracks.add(season["seasonRankingTrackId"])
    if not current_tracks:
        raise IntegrationError("El proveedor no identificó una temporada competitiva vigente. No se actualizaron los rangos.")
    entry = next((item for item in progress.get("modes", []) if item["rankingType"] == data.queue and item["rankingTrackId"] in current_tracks), None)
    current = (entry or {}).get("currentDivision") or {}
    peak = (entry or {}).get("highestDivision") or {}
    return {"current_rank": current.get("divisionName") or "Sin clasificación", "peak_rank": peak.get("divisionName"), "peak_scope": "Temporada actual", "rank_points": (entry or {}).get("promotionProgress"), "queue": "Battle Royale" if data.queue == "ranked-br" else "Cero construcción", "provider": "Osirion", "source_url": "https://dev.fnapi.osirion.gg/", "note": "Rango de la temporada actual de un proveedor independiente de Epic Games.", "status": "synced" if current else "unranked"}
