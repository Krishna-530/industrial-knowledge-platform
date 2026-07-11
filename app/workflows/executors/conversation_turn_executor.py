from typing import AsyncGenerator, Any, List
from app.conversation.models.message import MessageCreate
from app.conversation.models.conversation_turn import ConversationTurn
from app.conversation.conversation_service import ConversationService
from app.workflows.retrieval_workflow import RetrievalWorkflow
from app.workflows.context_workflow import ContextWorkflow
from app.workflows.prompt_workflow import PromptWorkflow
from app.workflows.llm_workflow import LLMWorkflow
from app.workflows.tool_workflow import ToolWorkflow
from app.conversation.models.conversation_config import ConversationConfig
from app.tools.models.tool_context import ToolContext
from app.llm.models.response import StreamChunk, ToolCallRequest
import time
import json

class ConversationTurnExecutor:
    def __init__(
        self,
        conversation_service: ConversationService,
        retrieval_workflow: RetrievalWorkflow,
        context_workflow: ContextWorkflow,
        prompt_workflow: PromptWorkflow,
        llm_workflow: LLMWorkflow,
        tool_workflow: ToolWorkflow,
        config: ConversationConfig
    ):
        self.conversation_service = conversation_service
        self.retrieval_workflow = retrieval_workflow
        self.context_workflow = context_workflow
        self.prompt_workflow = prompt_workflow
        self.llm_workflow = llm_workflow
        self.tool_workflow = tool_workflow
        self.config = config

    async def execute_turn_stream(self, conversation_id: str, user_message_id: str, expected_version: int) -> AsyncGenerator[Any, None]:
        iteration = 0
        
        turn = ConversationTurn(
            conversation_id=conversation_id,
            user_message_id=user_message_id,
        )
        start_time = time.time()
        
        conversation = await self.conversation_service.get_conversation(conversation_id)
        tool_context = ToolContext(
            user_id=conversation.user_id,
            workspace_id=conversation.workspace_id,
            conversation_id=conversation_id
        )
        
        # Iterative Loop for Tool execution
        while iteration < self.config.max_tool_iterations:
            iteration += 1
            
            history = await self.conversation_service.get_messages(conversation_id)
            prompt_payload = None 
            
            aggregated_content = []
            tool_call_requests = []
            interrupted = False
            
            try:
                async for chunk in self.llm_workflow.stream(prompt_payload):
                    if isinstance(chunk, StreamChunk):
                        if chunk.content_delta:
                            aggregated_content.append(chunk.content_delta)
                        if chunk.finish_reason and chunk.finish_reason.value == "tool_call" and chunk.tool_call_delta:
                            tool_call_requests.append(chunk.tool_call_delta)
                    yield chunk
            except Exception as e:
                interrupted = True
                
            final_content = "".join(aggregated_content)
            
            # Format tool calls in content if they exist for persistence
            if tool_call_requests:
                # We could serialize tool requests for DB storage, but we'll just save them as part of the message for simplicity
                final_content += f"\n[Tool Calls: {json.dumps([req.model_dump() for req in tool_call_requests])}]"
            
            assistant_msg_data = MessageCreate(
                role="assistant",
                content=final_content
            )
            
            assistant_message = await self.conversation_service.add_message(
                conversation_id=conversation_id,
                data=assistant_msg_data,
                expected_version=expected_version
            )
            expected_version += 1 # Advance version since we wrote to conversation
            
            if interrupted:
                assistant_message.interrupted = True
                break 
                
            if tool_call_requests:
                # 6. Execute Tools
                tool_results = await self.tool_workflow.execute_tools(tool_call_requests, tool_context)
                
                # 7. Persist Tool Results
                for res in tool_results:
                    tool_msg_data = MessageCreate(
                        role="tool",
                        content=res.content,
                        metadata={"tool_call_id": res.tool_call_id, "tool_name": res.tool_name, "is_error": res.is_error}
                    )
                    await self.conversation_service.add_message(
                        conversation_id=conversation_id,
                        data=tool_msg_data,
                        expected_version=expected_version
                    )
                    expected_version += 1
                    
                # Loop back to LLM to formulate final response based on tool results
                continue
            
            # No tool calls, conversation turn is done
            break

        turn.assistant_message_id = assistant_message.id
        turn.latency_ms = (time.time() - start_time) * 1000
        turn.tool_calls_executed = iteration - 1
        
        await self.conversation_service.turn_repo.create(turn)
