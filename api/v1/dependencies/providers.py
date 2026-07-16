# Compatibility façade for dependency providers
# Do not add new logic here. Use the modular providers instead.

from api.v1.dependencies.settings import provide_settings
from api.v1.dependencies.repositories import (
    provide_document_repo,
    provide_document_version_repo,
    provide_content_repo,
)
from api.v1.dependencies.services import (
    provide_storage_service,
    provide_event_publisher,
    provide_document_service,
    provide_content_service,
    provide_processing_service,
    provide_knowledge_fact_service,
    provide_knowledge_intelligence_service,
    provide_knowledge_analytics_service,
    provide_dashboard_service,
)
from api.v1.dependencies.workflows import (
    provide_document_upload_workflow,
    provide_document_processing_workflow,
)
from api.v1.dependencies.workers import (
    provide_worker_queue,
    provide_job_executor_factory,
    provide_execution_boundary,
    provide_document_worker,
    provide_worker_manager,
)
from api.v1.dependencies.search import (
    provide_search_provider,
    provide_search_service,
    provide_indexing_service,
    provide_search_workflow,
    provide_indexing_workflow,
)
from api.v1.dependencies.retrieval import (
    provide_authorization_service,
    provide_retrieval_strategy,
    provide_retrieval_ranker,
    provide_knowledge_assembler,
    provide_retrieval_service,
    provide_retrieval_workflow
)
from api.v1.dependencies.context import (
    provide_token_counter,
    provide_packing_strategy,
    provide_formatters,
    provide_chunk_extractor,
    provide_chunk_selector,
    provide_context_compressor,
    provide_context_ranker,
    provide_context_budgeter,
    provide_context_service,
    provide_context_workflow
)
from api.v1.dependencies.prompt import (
    provide_template_registry,
    provide_template_resolver,
    provide_prompt_renderer,
    provide_variable_validator,
    provide_prompt_validator,
    provide_message_ordering_strategy,
    provide_prompt_service,
    provide_prompt_workflow
)

__all__ = [
    "provide_settings",
    "provide_document_repo",
    "provide_document_version_repo",
    "provide_content_repo",
    "provide_storage_service",
    "provide_event_publisher",
    "provide_document_service",
    "provide_content_service",
    "provide_processing_service",
    "provide_knowledge_fact_service",
    "provide_knowledge_intelligence_service",
    "provide_document_upload_workflow",
    "provide_document_processing_workflow",
    "provide_worker_queue",
    "provide_job_executor_factory",
    "provide_execution_boundary",
    "provide_document_worker",
    "provide_worker_manager",
    "provide_search_provider",
    "provide_search_service",
    "provide_indexing_service",
    "provide_search_workflow",
    "provide_indexing_workflow",
    "provide_authorization_service",
    "provide_retrieval_strategy",
    "provide_retrieval_ranker",
    "provide_knowledge_assembler",
    "provide_retrieval_service",
    "provide_retrieval_workflow",
    "provide_token_counter",
    "provide_packing_strategy",
    "provide_formatters",
    "provide_chunk_extractor",
    "provide_chunk_selector",
    "provide_context_compressor",
    "provide_context_ranker",
    "provide_context_budgeter",
    "provide_context_service",
    "provide_context_workflow",
    "provide_template_registry",
    "provide_template_resolver",
    "provide_prompt_renderer",
    "provide_variable_validator",
    "provide_prompt_validator",
    "provide_message_ordering_strategy",
    "provide_prompt_service",
    "provide_prompt_workflow"
]
