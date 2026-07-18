from fastapi import Depends
from app.context.schemas import ContextFormat
from app.context.interfaces import AbstractTokenCounter, AbstractContextFormatter, AbstractPackingStrategy
from app.context.counters.heuristic_counter import HeuristicTokenCounter
from app.context.formatters.xml_formatter import XMLContextFormatter
from app.context.formatters.markdown_formatter import MarkdownContextFormatter
from app.context.pipeline.chunk_extractor import ChunkExtractor
from app.context.pipeline.chunk_selector import ChunkSelector
from app.context.pipeline.context_compressor import ContextCompressor
from app.context.pipeline.context_ranker import ContextRanker
from app.context.pipeline.context_budgeter import ContextBudgeter
from app.context.pipeline.greedy_packing import GreedyPackingStrategy
from app.context.context_service import ContextService
from app.workflows.context_workflow import ContextWorkflow
from api.v1.dependencies.retrieval import provide_retrieval_workflow
from app.workflows.retrieval_workflow import RetrievalWorkflow

def provide_token_counter() -> AbstractTokenCounter:
    return HeuristicTokenCounter()

def provide_packing_strategy() -> AbstractPackingStrategy:
    return GreedyPackingStrategy()

def provide_formatters() -> dict[ContextFormat, AbstractContextFormatter]:
    return {
        ContextFormat.XML: XMLContextFormatter(),
        ContextFormat.MARKDOWN: MarkdownContextFormatter()
    }

def provide_chunk_extractor() -> ChunkExtractor:
    return ChunkExtractor()

def provide_chunk_selector() -> ChunkSelector:
    return ChunkSelector()

def provide_context_compressor() -> ContextCompressor:
    return ContextCompressor()

def provide_context_ranker() -> ContextRanker:
    return ContextRanker()

def provide_context_budgeter(
    packing_strategy: AbstractPackingStrategy = Depends(provide_packing_strategy),
    token_counter: AbstractTokenCounter = Depends(provide_token_counter)
) -> ContextBudgeter:
    return ContextBudgeter(packing_strategy, token_counter)

def provide_context_service(
    extractor: ChunkExtractor = Depends(provide_chunk_extractor),
    selector: ChunkSelector = Depends(provide_chunk_selector),
    compressor: ContextCompressor = Depends(provide_context_compressor),
    ranker: ContextRanker = Depends(provide_context_ranker),
    budgeter: ContextBudgeter = Depends(provide_context_budgeter),
    formatters: dict = Depends(provide_formatters)
) -> ContextService:
    return ContextService(
        extractor=extractor,
        selector=selector,
        compressor=compressor,
        ranker=ranker,
        budgeter=budgeter,
        formatters=formatters
    )

def provide_context_workflow(
    retrieval_workflow: RetrievalWorkflow = Depends(provide_retrieval_workflow),
    context_service: ContextService = Depends(provide_context_service)
) -> ContextWorkflow:
    return ContextWorkflow(retrieval_workflow, context_service)
