from pydantic_settings import BaseSettings

class GroqConfig(BaseSettings):
    api_key: str
    base_url: str = "https://api.groq.com/openai/v1"
    connect_timeout: float = 5.0
    read_timeout: float = 60.0
    write_timeout: float = 10.0
    total_timeout: float = 120.0
    max_connections: int = 100

    class Config:
        env_prefix = "GROQ_"
        env_file = ".env"
