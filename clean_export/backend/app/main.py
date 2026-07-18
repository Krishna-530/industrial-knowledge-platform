import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure initial simple logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

def create_app() -> FastAPI:
    """Application factory for the FastAPI system."""
    app = FastAPI(
        title="Industrial Knowledge Intelligence Platform",
        description="AI-Powered Asset & Operations Brain",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # To be restricted in production config
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["Monitoring"])
    async def health_check() -> dict[str, str]:
        """Liveness/readiness probe for container orchestration."""
        return {
            "status": "healthy",
            "version": "0.1.0"
        }

    return app

app = create_app()
