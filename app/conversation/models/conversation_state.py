from enum import Enum

class ConversationState(str, Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    EVALUATING = "EVALUATING"
    RESPONDING = "RESPONDING"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"
    FAILED = "FAILED"
