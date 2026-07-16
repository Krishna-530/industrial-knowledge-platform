import enum

class EntityStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PENDING_REVIEW = "PENDING_REVIEW"
    MERGED = "MERGED"
    DELETED = "DELETED"
