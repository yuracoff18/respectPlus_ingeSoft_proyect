from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.config import ALLOWED_ORIGINS


def install_middleware(app):
    app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=True, allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type"])

    @app.middleware("http")
    async def protect_origin(request, call_next):
        origin = request.headers.get("origin")
        if request.method not in ("GET", "HEAD", "OPTIONS") and origin and origin not in ALLOWED_ORIGINS:
            return JSONResponse({"detail": "Origen no permitido."}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response
