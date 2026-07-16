from pydantic_settings import BaseSettings

class ConversationConfig(BaseSettings):
    max_tool_iterations: int = 5
    max_history_tokens: int = 4096
    max_context_tokens: int = 8192
    summary_threshold_percent: float = 0.8
    
    class Config:
        env_prefix = "CONVERSATION_"
        env_file = ".env"
