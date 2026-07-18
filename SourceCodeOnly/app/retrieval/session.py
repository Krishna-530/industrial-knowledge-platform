import uuid
import time
from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from app.retrieval.planners.dto import RetrievalPlan, RankingProfileType
import logging

logger = logging.getLogger(__name__)

class RetrievalState(str, Enum):
    PLANNING = "PLANNING"
    VALIDATING = "VALIDATING"
    RESOLVING = "RESOLVING"
    GRAPH_EXECUTION = "GRAPH_EXECUTION"
    SEMANTIC_EXECUTION = "SEMANTIC_EXECUTION"
    KEYWORD_EXECUTION = "KEYWORD_EXECUTION"
    FUSION = "FUSION"
    BUDGETING = "BUDGETING"
    PROMPT_BUILDING = "PROMPT_BUILDING"
    COMPLETED = "COMPLETED"
    DEGRADED = "DEGRADED"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"

class PipelineVersionRegistry(BaseModel):
    planner_version: str = "v1.0"
    policy_version: str = "v1.0"
    graph_version: str = "v1.0"
    ranking_version: str = "v1.0"
    retrieval_pipeline_version: str = "v1.0"
    prompt_version: str = "v1.0"

class RetrievalSession(BaseModel):
    """
    The singular state object flowing through the entire 15-stage Retrieval Pipeline.
    """
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str
    tenant_id: str
    user_id: str
    
    # State tracking
    current_state: RetrievalState = RetrievalState.PLANNING
    
    # Versions
    versions: PipelineVersionRegistry = Field(default_factory=PipelineVersionRegistry)
    
    # Core Data
    original_query: str
    rewritten_query: Optional[str] = None
    
    # Output from Planner
    plan: Optional[RetrievalPlan] = None
    
    # Budgets
    graph_budget: int = 0
    semantic_budget: int = 0
    keyword_budget: int = 0
    
    # Execution Tracking
    cache_metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_timings: Dict[str, float] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    telemetry_context: Dict[str, Any] = Field(default_factory=dict)
    
    # Internal timer for state transitions
    _state_start_time: float = 0.0

    def transition(self, new_state: RetrievalState) -> None:
        """
        Transitions the state machine and emits telemetry.
        """
        now = time.time()
        if self._state_start_time > 0:
            duration_ms = (now - self._state_start_time) * 1000
            self.execution_timings[self.current_state.value] = duration_ms
            logger.info(f"RetrievalSession {self.request_id} | {self.current_state.value} -> {new_state.value} ({duration_ms:.2f}ms)")
        else:
            logger.info(f"RetrievalSession {self.request_id} | Initialized -> {new_state.value}")
            
        self.current_state = new_state
        self._state_start_time = now

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)
        logger.warning(f"RetrievalSession {self.request_id} WARNING: {warning}")

    class Config:
        arbitrary_types_allowed = True
