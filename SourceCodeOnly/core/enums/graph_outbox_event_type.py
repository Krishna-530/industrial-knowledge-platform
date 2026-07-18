import enum

class GraphOutboxEventType(str, enum.Enum):
    NODE_UPSERT = "NODE_UPSERT"
    EDGE_UPSERT = "EDGE_UPSERT"
    NODE_DELETE = "NODE_DELETE"
    EDGE_DELETE = "EDGE_DELETE"
