"""FastAPI application factory for Constellation API.

Architecture:
- Routes are thin (no business logic)
- Services own business logic
- Repositories own data access
- Pydantic schemas validate at boundaries

See BACKEND_ARCHITECTURE.md for the full design.
"""

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.database import verify_database_connection
from app.core.error_handlers import register_error_handlers
from app.core.logging import configure_logging, logger

# ── Application Startup Timestamp ────────────────────────────────────────

_START_TIME = time.monotonic()


# ── App Factory ───────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="Constellation API",
        description="Social timetable platform for college students",
        version=settings.VERSION,
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    )

    # ── Middleware ────────────────────────────────────────────────────────
    # Order matters: first registered = outermost

    app.add_middleware(
        CORSMiddleware,
        allow_origins=(
            settings.CORS_ORIGINS
            if settings.CORS_ORIGINS
            else [str(settings.FRONTEND_URL)]
        ),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    # ── Routers ──────────────────────────────────────────────────────────

    app.include_router(api_v1_router)

    # ── Global Health Endpoint ───────────────────────────────────────────

    @app.get("/api/v1/health", tags=["System"])
    async def health_check(request: Request) -> JSONResponse:
        db_status = await verify_database_connection()
        uptime = round(time.monotonic() - _START_TIME, 1)
        return JSONResponse(content={
            "status": "healthy" if db_status["status"] == "healthy" else "degraded",
            "version": settings.VERSION,
            "uptime_seconds": uptime,
            "database": db_status,
        })

    # ── Error Handlers ───────────────────────────────────────────────────

    register_error_handlers(app)

    # ── Lifecycle Events ─────────────────────────────────────────────────

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info(
            "Constellation API starting",
            extra={"environment": settings.ENVIRONMENT, "version": settings.VERSION},
        )

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        from app.core.database import dispose_database_engine
        await dispose_database_engine()
        logger.info("Constellation API shutdown complete")

    return app


app = create_app()
