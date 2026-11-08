import os
import re
from urllib.parse import urlencode
from .http import IntegrationError, get_json


def fetch(data, client=get_json):
    key = os.getenv("STEAM_WEB_API_KEY")
    if not key:
        raise IntegrationError("Falta configurar la clave Web API de Steam.", "not_configured")
    if not re.fullmatch(r"[0-9]{17}", data.identifier):
        raise IntegrationError("Para Steam, introduce un SteamID64 de 17 dígitos.")
    response = client("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?" + urlencode({"key": key, "steamids": data.identifier}))
    players = response.get("response", {}).get("players", [])
    if not players:
        raise IntegrationError("No encontramos esa cuenta de Steam.")
    return {"current_rank": None, "peak_rank": None, "provider_account_name": players[0].get("personaname"), "provider": "Steam Web API", "source_url": "https://partner.steamgames.com/doc/webapi/ISteamUser", "note": "Cuenta encontrada en Steam. La Web API no proporciona el rango Premier ni su pico de Counter-Strike 2.", "status": "unavailable"}
