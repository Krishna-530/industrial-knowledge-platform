from fastapi import Depends
from app.tools.registry import ToolRegistry
from app.tools.security.permission_evaluator import ToolPermissionEvaluator
from app.tools.tool_service import ToolService
from app.workflows.tool_workflow import ToolWorkflow

from app.tools.models.tool_manifest import ToolManifest, ToolCategory
from app.tools.interfaces.tool_factory import ToolFactory

from app.tools.implementations.calculator_tool import CalculatorTool
from app.tools.implementations.datetime_tool import DateTimeTool
from app.tools.implementations.system_info_tool import SystemInfoTool
from app.tools.implementations.knowledge_search_tool import KnowledgeSearchTool
from app.tools.implementations.document_reader_tool import DocumentReaderTool
from app.tools.implementations.conversation_search_tool import ConversationSearchTool

class SimpleFactory(ToolFactory):
    def __init__(self, tool_class, *args, **kwargs):
        self.tool_class = tool_class
        self.args = args
        self.kwargs = kwargs
    def create(self):
        return self.tool_class(*self.args, **self.kwargs)

def provide_tool_registry(
    # In real wiring, workflows and services would be injected here 
    # and passed to the factories. For phase 8.2 orchestrator setup, 
    # we just instantiate with None or dummy instances for the service-backed tools.
) -> ToolRegistry:
    registry = ToolRegistry()
    
    # 1. Calculator
    registry.register(
        ToolManifest(
            id="calculator",
            display_name="Calculator",
            description="Evaluates mathematical expressions safely",
            category=ToolCategory.UTILITY,
            parameters_schema={"type": "object", "properties": {"expression": {"type": "string"}}}
        ),
        SimpleFactory(CalculatorTool)
    )
    
    # 2. DateTime
    registry.register(
        ToolManifest(
            id="datetime",
            display_name="Date & Time",
            description="Returns the current UTC date and time",
            category=ToolCategory.UTILITY,
            parameters_schema={"type": "object", "properties": {}}
        ),
        SimpleFactory(DateTimeTool)
    )
    
    # 3. System Info
    registry.register(
        ToolManifest(
            id="system_info",
            display_name="System Information",
            description="Returns safe capability flags and API versions",
            category=ToolCategory.SYSTEM,
            parameters_schema={"type": "object", "properties": {}}
        ),
        SimpleFactory(SystemInfoTool)
    )
    
    # 4. Knowledge Search
    registry.register(
        ToolManifest(
            id="knowledge_search",
            display_name="Knowledge Search",
            description="Searches the workspace knowledge base for documents answering the query",
            category=ToolCategory.KNOWLEDGE,
            parameters_schema={"type": "object", "properties": {"query": {"type": "string"}}}
        ),
        SimpleFactory(KnowledgeSearchTool, None) # None for retrieval_workflow
    )
    
    # 5. Document Reader
    registry.register(
        ToolManifest(
            id="document_reader",
            display_name="Document Reader",
            description="Reads the full content of a specific document by ID",
            category=ToolCategory.KNOWLEDGE,
            parameters_schema={"type": "object", "properties": {"document_id": {"type": "string"}}}
        ),
        SimpleFactory(DocumentReaderTool, None) # None for document_service
    )
    
    # 6. Conversation Search
    registry.register(
        ToolManifest(
            id="conversation_search",
            display_name="Conversation Search",
            description="Searches past messages in the current conversation",
            category=ToolCategory.CONVERSATION,
            parameters_schema={"type": "object", "properties": {"query": {"type": "string"}}}
        ),
        SimpleFactory(ConversationSearchTool, None, None) # None for strategy and service
    )
    
    return registry

def provide_permission_evaluator() -> ToolPermissionEvaluator:
    return ToolPermissionEvaluator()

def provide_tool_service(
    registry: ToolRegistry = Depends(provide_tool_registry),
    evaluator: ToolPermissionEvaluator = Depends(provide_permission_evaluator)
) -> ToolService:
    return ToolService(registry, evaluator)

def provide_tool_workflow(
    service: ToolService = Depends(provide_tool_service)
) -> ToolWorkflow:
    return ToolWorkflow(service)
