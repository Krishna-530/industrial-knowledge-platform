from fastapi import Depends
from core.settings import get_settings, Settings

def provide_settings() -> Settings:
    return get_settings()
