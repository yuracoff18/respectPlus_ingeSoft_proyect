"""Prepare a private local .env with a cryptographically random admin password."""
import argparse
import json
from pathlib import Path
import secrets
import string

ROOT = Path(__file__).resolve().parents[1]


def prepare(rotate=False):
    path = ROOT / "Docker" / ".env"
    if not path.exists():
        path.write_text((ROOT / "Docker" / ".env.example").read_text(encoding="utf-8-sig"), encoding="utf-8")
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    values = dict(line.split("=", 1) for line in lines if "=" in line and not line.lstrip().startswith("#"))
    password = values.get("BOOTSTRAP_ADMIN_PASSWORD", "")
    if rotate or not password:
        chars = [secrets.choice(string.ascii_lowercase), secrets.choice(string.ascii_uppercase), secrets.choice(string.digits), secrets.choice("!@%_-")]
        chars.extend(secrets.choice(string.ascii_letters + string.digits + "!@%_-") for _ in range(28))
        secrets.SystemRandom().shuffle(chars)
        password = "".join(chars)
    replacements = {"BOOTSTRAP_ADMIN_USERNAME": "admin", "BOOTSTRAP_ADMIN_EMAIL": "admin@respect.local", "BOOTSTRAP_ADMIN_PASSWORD": password}
    output = [line for line in lines if not line.startswith("SEED_DEMO=") and not any(line.startswith(key + "=") for key in replacements)]
    path.write_text("\n".join(output + [f"{key}={value}" for key, value in replacements.items()]) + "\n", encoding="utf-8")
    return {"username": "admin", "password": password}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rotate", action="store_true")
    parser.add_argument("--print-credentials", action="store_true")
    args = parser.parse_args()
    credentials = prepare(args.rotate)
    print(json.dumps(credentials) if args.print_credentials else "Configuración privada de administración preparada en Docker/.env.")
