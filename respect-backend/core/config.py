import os

GAMES = ["Valorant", "League of Legends", "Counter-Strike 2", "Rocket League", "Fortnite", "EA Sports FC"]
ALLOWED_ORIGINS = [value.strip() for value in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if value.strip()]
SESSION_SECONDS = 60 * 60 * 24 * 7
