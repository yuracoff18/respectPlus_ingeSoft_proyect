import hashlib
import os
import secrets
import time
from collections import defaultdict, deque
from fastapi import HTTPException
from core.config import SESSION_SECONDS
from store import lock

attempts: dict[str, deque] = defaultdict(deque)


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
    return f"{salt}:{digest}"


def set_session(repository, response, user):
    token = secrets.token_urlsafe(32)
    now = time.time()
    repository.delete_expired(now)
    repository.save_session({"id": hashlib.sha256(token.encode()).hexdigest(), "user_id": user["id"], "expires_at": now + SESSION_SECONDS})
    response.set_cookie("respect_session", token, httponly=True, secure=os.getenv("COOKIE_SECURE", "false").lower() == "true", samesite="lax", max_age=SESSION_SECONDS, path="/")


def rate_limit(request):
    key = request.client.host if request.client else "local"
    now = time.monotonic()
    with lock:
        for address in list(attempts):
            while attempts[address] and now - attempts[address][0] > 300:
                attempts[address].popleft()
            if not attempts[address]:
                del attempts[address]
        bucket = attempts[key]
        if len(bucket) >= 30:
            raise HTTPException(429, "Demasiados intentos. Espera unos minutos e inténtalo de nuevo.")
        bucket.append(now)
