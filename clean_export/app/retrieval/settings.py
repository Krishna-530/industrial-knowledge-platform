from pydantic_settings import BaseSettings

class RetrievalFeatureFlags(BaseSettings):
    """
    Granular operational controls to manage deployment risk and system load.
    """
    GRAPH_ENABLED: bool = True
    GRAPH_CACHE_ENABLED: bool = True
    GRAPH_TRAVERSAL_ENABLED: bool = True
    GRAPH_PLANNER_ENABLED: bool = True
    GRAPH_CONTEXT_BUDGET_ENABLED: bool = True
    GRAPH_EXPLAINABILITY_ENABLED: bool = True
    ENTITY_RESOLUTION_ENABLED: bool = True

    class Config:
        env_prefix = "RAG_"

settings = RetrievalFeatureFlags()
