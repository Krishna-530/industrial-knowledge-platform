from fastapi import Depends
from app.llm.providers.registry import ProviderRegistry
from app.llm.providers.groq_provider import GroqProvider
from app.llm.providers.groq_config import GroqConfig
from app.llm.providers.normalizers.groq_normalizer import GroqResponseNormalizer, GroqStreamNormalizer
from app.llm.pipeline.stages.validation_stage import ValidationStage
from app.llm.pipeline.stages.model_selection_stage import ModelSelectionStage
from app.llm.pipeline.stages.health_stage import HealthStage
from app.llm.pipeline.stages.execution_stage import ExecutionStage
from app.llm.pipeline.middleware.logging_middleware import LoggingMiddleware
from app.llm.pipeline.stream.stream_assembler import StreamAssembler
from app.llm.pipeline.stream.stream_normalizer import StreamNormalizerMiddleware
from app.llm.pipeline.orchestrator import LLMExecutionPipeline
from app.workflows.llm_workflow import LLMWorkflow
from app.llm.pipeline.retry_policy import RetryPolicy
from app.llm.pipeline.retry_classifier import RetryClassifier
from app.llm.pipeline.token_estimator import TokenEstimator

def provide_groq_config() -> GroqConfig:
    return GroqConfig()

def provide_provider_registry(groq_config: GroqConfig = Depends(provide_groq_config)) -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register(GroqProvider(groq_config))
    return registry

def provide_llm_pipeline(registry: ProviderRegistry = Depends(provide_provider_registry)) -> LLMExecutionPipeline:
    retry_policy = RetryPolicy()
    retry_classifier = RetryClassifier()
    token_estimator = TokenEstimator()
    stages = [
        ValidationStage(token_estimator),
        ModelSelectionStage(registry),
        HealthStage(registry),
        ExecutionStage(registry, retry_policy, retry_classifier)
    ]
    middlewares = [
        LoggingMiddleware()
    ]
    return LLMExecutionPipeline(stages, middlewares)

def provide_llm_workflow(pipeline: LLMExecutionPipeline = Depends(provide_llm_pipeline)) -> LLMWorkflow:
    response_normalizer = GroqResponseNormalizer()
    stream_normalizer = GroqStreamNormalizer()
    return LLMWorkflow(pipeline, response_normalizer, stream_normalizer)
