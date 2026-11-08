"""Create the first administrator from server configuration; never seed demo data."""
import os
import re
from uuid import uuid4
from core.security import password_hash
from store import lock


def validate_admin_password(value):
    if len(value) < 20 or len(value) > 128 or not all(re.search(pattern, value) for pattern in (r"[a-z]", r"[A-Z]", r"[0-9]", r"[^A-Za-z0-9]")):
        raise ValueError("La contraseña administradora debe tener 20–128 caracteres, mayúsculas, minúsculas, números y símbolos.")
    return value


def bootstrap_admin(store):
    with lock:
        if any(user.get("role") == "admin" for user in store.all("users")):
            return None
        password = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")
        if not password:
            return None
        validate_admin_password(password)
        username = os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin").lower()
        if not re.fullmatch(r"[a-z0-9_]{3,24}", username):
            raise ValueError("BOOTSTRAP_ADMIN_USERNAME inválido")
        if any(user["username"].casefold() == username for user in store.all("users")):
            raise ValueError("El usuario inicial de administración ya está ocupado")
        user = {"id": str(uuid4()), "username": username, "name": "Administración Respect+", "email": os.getenv("BOOTSTRAP_ADMIN_EMAIL", "admin@respect.local").lower(), "role": "admin", "password_hash": password_hash(password), "headline": "Moderación de la comunidad", "bio": "", "games": [], "game": "", "country": "Colombia", "available": False, "color": "#c1515d", "connections": [], "game_profiles": {}, "banned": False}
        return store.put("users", user)
