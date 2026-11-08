import os
from urllib.parse import urlencode
from .http import IntegrationError, get_json


def fetch(data, client=get_json):
    key = os.getenv("FACEIT_API_KEY")
    if not key:
        raise IntegrationError("Falta configurar la clave de FACEIT para Counter-Strike 2.", "not_configured")
    response = client("https://open.faceit.com/data/v4/players?" + urlencode({"nickname": data.identifier}), {"Authorization": f"Bearer {key}"})
    stats = response.get("games", {}).get("cs2")
    if not stats:
        raise IntegrationError("Esta cuenta no tiene clasificación de Counter-Strike 2 en FACEIT.")
    return {"current_rank": f"FACEIT nivel {stats['skill_level']}", "peak_rank": None, "rank_points": stats.get("faceit_elo"), "queue": "FACEIT · No es Premier", "provider": "FACEIT", "source_url": "https://docs.faceit.com/docs/data-api/data/", "note": "Nivel y Elo de FACEIT. No equivalen al rango Premier de Valve.", "status": "synced"}
