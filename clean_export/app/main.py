from fastapi import FastAPI
from core.settings import Settings
from app.lifespan import lifespan
from middleware.cors import setup_cors
from middleware.request_id import RequestIDMiddleware
from middleware.timing import TimingMiddleware
from middleware.error_handler import setup_exception_handlers
from api.v1.router import api_router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = Settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    # Configure middleware (order matters)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIDMiddleware)
    setup_cors(app, settings)

    # Configure exception handlers
    setup_exception_handlers(app)

    # Include routers
    app.include_router(api_router, prefix="/api/v1")

    return app

app = create_app()
