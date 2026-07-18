from functools import lru_cache
from core.settings import Settings

@lru_cache()
def get_settings() -> Settings:
    """Return application settings as a singleton."""
    return Settings()
