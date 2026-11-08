"""Read provider credentials through stdin and save only to ignored Docker/.env."""
import json
from pathlib import Path
import sys
import getpass

allowed = {"RIOT_API_KEY", "STEAM_WEB_API_KEY", "HENRIK_API_KEY", "FACEIT_API_KEY", "FORTNITE_API_KEY"}
print("Ready for provider configuration on stdin.", flush=True)
values = json.loads(getpass.getpass("") if sys.stdin.isatty() else sys.stdin.readline())
if set(values) - allowed:
    raise ValueError("Unsupported configuration key")
path = Path(__file__).resolve().parents[1] / "Docker" / ".env"
lines = path.read_text(encoding="utf-8-sig").splitlines()
lines = [line for line in lines if not any(line.startswith(key + "=") for key in values)]
for value in values.values():
    if "\n" in value or "\r" in value:
        raise ValueError("Invalid credential format")
path.write_text("\n".join(lines + [f"{key}={value}" for key, value in values.items()]) + "\n", encoding="utf-8")
print("Provider configuration saved without printing credentials.")
