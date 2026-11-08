"""Application composition. Business rules live in modules/<domain>/services."""
from fastapi import FastAPI
from core.health import router as health_router
from core.lifespan import lifespan
from core.middleware import install_middleware
from modules.auth.controller.routes import router as auth_router
from modules.players.controller.routes import router as players_router
from modules.publications.controller.routes import router as publications_router
from modules.teams.controller.routes import router as teams_router
from modules.sponsors.controller.routes import router as sponsors_router
from modules.tournaments.controller.routes import router as tournaments_router
from modules.reports.controller.routes import router as reports_router
from modules.admins.controller.routes import router as admins_router
from modules.game_accounts.controller.routes import router as game_accounts_router

app = FastAPI(title="Respect+ API", version="2.0.0", lifespan=lifespan)
install_middleware(app)
for router in (health_router, auth_router, players_router, publications_router, teams_router, sponsors_router, tournaments_router, reports_router, admins_router, game_accounts_router):
    app.include_router(router)
