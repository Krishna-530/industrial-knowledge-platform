from enum import Enum

class ConversationState(str, Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    STREAMING = "STREAMING"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"
    FAILED = "FAILED"
