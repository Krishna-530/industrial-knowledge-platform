from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings and configuration."""
    app_name: str = "Industrial Knowledge Intelligence Platform API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or standard
    
    # CORS
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 7

    # Database
    database_url: str
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_echo: bool = False

    # Storage
    upload_directory: str = "uploads"
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    allowed_mime_types: list[str] = [
        "application/pdf", 
        "text/plain", 
        "application/msword", 
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    max_filename_length: int = 255
    upload_chunk_size: int = 65536  # 64KB

    # Worker / Job Orchestration
    worker_id: str = "worker-1"
    worker_poll_interval: float = 2.0
    worker_max_attempts: int = 3
    worker_backoff_multiplier: int = 10
    worker_orphan_timeout_minutes: int = 60
    worker_job_timeout_seconds: int = 300

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
