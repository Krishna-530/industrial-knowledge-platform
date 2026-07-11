from pydantic import BaseModel

class RetryPolicy(BaseModel):
    max_retries: int = 3
    base_backoff_ms: int = 1000
    max_backoff_ms: int = 10000
