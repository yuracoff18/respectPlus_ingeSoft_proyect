"""Read the private key from .env; only print access diagnostics."""
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

path = Path(__file__).resolve().parents[1] / "Docker" / ".env"
values = dict(line.split("=", 1) for line in path.read_text(encoding="utf-8-sig").splitlines() if "=" in line and not line.lstrip().startswith("#"))
key = values.get("FORTNITE_API_KEY", "")
if not key:
    raise SystemExit("Fortnite provider key is not configured")

for label, endpoint in [("Ranked access", "/api/v1/profile/ranked?accountId=00000000000000000000000000000000"), ("Ranked tracks metadata", "/api/v1/profile/tracks")]:
    try:
        request = Request("https://prod.api-fortnite.com" + endpoint, headers={"x-api-key": key, "Accept": "application/json", "User-Agent": "RespectPlus/3.0"})
        with build_opener(NoRedirect).open(request, timeout=8) as response:
            data = json.loads(response.read(1_000_000))
            print(json.dumps({"check": label, "status": response.status, "shape": list(data)[:15] if isinstance(data, dict) else "list"}))
            if "tracks" in endpoint:
                destination = path.parents[1] / "tmp" / "api-docs" / "fortnite-tracks.json"
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(json.dumps(data), encoding="utf-8")
    except HTTPError as error:
        with error:
            # Do not print URLs, headers, credentials or unfiltered error bodies.
            body = error.read(2000)
            try:
                data = json.loads(body)
                message = data.get("error") or data.get("message") or data.get("title") or "Provider rejected request"
            except ValueError:
                message = "Provider rejected request"
            if message not in ("API key required", "Invalid or inactive API key"):
                message = "Provider rejected request"
            print(json.dumps({"check": label, "status": error.code, "message": str(message)[:250]}))
    except (URLError, TimeoutError, ValueError):
        print(json.dumps({"check": label, "status": "unavailable"}))
