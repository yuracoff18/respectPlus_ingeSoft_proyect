"""Verify only provider access, never print keys or account data."""
import argparse
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

path = Path(__file__).resolve().parents[1] / "Docker" / ".env"
values = dict(line.split("=", 1) for line in path.read_text(encoding="utf-8-sig").splitlines() if "=" in line and not line.lstrip().startswith("#"))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def check(label, url, headers=None):
    try:
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "RespectPlus/3.0", **(headers or {})})
        with build_opener(NoRedirect).open(request, timeout=8) as response:
            print(f"{label}: HTTP {response.status}")
    except HTTPError as error:
        with error:
            print(f"{label}: HTTP {error.code}")
    except (URLError, TimeoutError):
        print(f"{label}: connection unavailable")


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--provider", choices=("riot", "henrik", "steam", "fortnite", "osirion"), help="Check only this provider; defaults to all.")
selected = parser.parse_args().provider

if selected in (None, "riot"):
    headers = {"X-Riot-Token": values.get("RIOT_API_KEY", "")}
    check("Riot Games (LAN status)", "https://la1.api.riotgames.com/lol/status/v4/platform-data", headers)
    check("League of Legends (LAN League-V4)", "https://la1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5", headers)
if selected in (None, "steam"):
    check("Steam (API access)", "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?" + urlencode({"key": values.get("STEAM_WEB_API_KEY", ""), "vanityurl": "respectplus-validation-no-account"}))
if selected in (None, "henrik"):
    check("Valorant HenrikDev (version metadata)", "https://api.henrikdev.xyz/valorant/v1/version/na", {"Authorization": values.get("HENRIK_API_KEY", "")})
if selected in (None, "fortnite"):
    check("Fortnite supplied endpoint (x-api-key)", "https://prod.api-fortnite.com/api/v1/profile/ranked?accountId=00000000000000000000000000000000", {"x-api-key": values.get("FORTNITE_API_KEY", "")})
if selected in (None, "osirion"):
    check("Fortnite Osirion ranked metadata", "https://dev.fnapi.osirion.gg/v1/ranked/modes?lang=es")
