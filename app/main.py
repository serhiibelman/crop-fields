from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.db import engine
from app.core.errors import register_exception_handlers
from app.fields.routers import router as fields_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Crop Fields API", version="0.1.0", lifespan=lifespan)
    register_exception_handlers(app)
    app.include_router(fields_router, prefix="/api")

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok"}

    return app


app = create_app()
