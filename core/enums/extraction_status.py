from enum import Enum

class ExtractionStatus(str, Enum):
    PROCESSING = "PROCESSING"
    EXTRACTED = "EXTRACTED"
    FAILED = "FAILED"
    RETRY_PENDING = "RETRY_PENDING"
