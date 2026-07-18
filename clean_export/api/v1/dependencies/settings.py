from core.settings import Settings
from functools import lru_cache

@lru_cache()
def get_settings() -> Settings:
    return Settings()

def provide_settings() -> Settings:
    return get_settings()
