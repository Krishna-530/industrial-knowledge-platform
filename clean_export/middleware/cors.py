from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.settings import Settings

def setup_cors(app: FastAPI, settings: Settings) -> None:
    """Configure CORS for the application."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
