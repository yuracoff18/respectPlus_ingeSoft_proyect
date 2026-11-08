from contextlib import asynccontextmanager
from core.bootstrap import bootstrap_admin
from store import Store


@asynccontextmanager
async def lifespan(app):
    app.state.store = Store()
    bootstrap_admin(app.state.store)
    try:
        yield
    finally:
        app.state.store.close()
