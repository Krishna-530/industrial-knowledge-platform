from pydantic_settings import BaseSettings

class ConversationConfig(BaseSettings):
    max_tool_iterations: int = 5
    max_history_tokens: int = 4096
    
    class Config:
        env_prefix = "CONVERSATION_"
        env_file = ".env"
