import logging
from app.conversation.events.events import ConversationSummaryRequested
from app.conversation.conversation_service import ConversationService
from app.workflows.llm_workflow import LLMWorkflow
from app.workflows.models.prompt_payload import PromptPayload

logger = logging.getLogger(__name__)

class SummaryProcessor:
    def __init__(self, conversation_service: ConversationService, llm_workflow: LLMWorkflow):
        self.conversation_service = conversation_service
        self.llm_workflow = llm_workflow
        self.max_retries = 3

    async def handle_summary_requested(self, event: ConversationSummaryRequested):
        payload = event.payload
        conversation_id = payload.get("conversation_id")
        expected_version = payload.get("expected_version")
        target_message_id = payload.get("target_message_id")
        
        # 1. Load conversation
        conversation = await self.conversation_service.get_conversation(conversation_id)
        if not conversation:
            logger.error(f"Conversation {conversation_id} not found.")
            return
            
        # 2. Idempotency Check: summary_version
        if conversation.summary_version != expected_version:
            logger.info(f"Discarding event: version mismatch. Expected {expected_version}, got {conversation.summary_version}")
            return
            
        # 3. Idempotency Check: summarized_up_to_message_id
        # In a real system, we might need a way to compare message IDs (e.g., creation timestamps or sequential IDs).
        # For simplicity, if target_message_id matches the current summarized_up_to, we discard.
        if conversation.summarized_up_to_message_id == target_message_id:
            logger.info(f"Discarding event: already summarized up to {target_message_id}")
            return
            
        # 4. Generate Incremental Summary
        # Fetch all messages
        all_messages = await self.conversation_service.get_messages(conversation_id)
        
        # Filter messages after the last summarized message
        new_messages = []
        capture = False if conversation.summarized_up_to_message_id else True
        for msg in all_messages:
            if capture:
                new_messages.append(msg)
            elif msg.id == conversation.summarized_up_to_message_id:
                capture = True
                
        # If no new messages, return
        if not new_messages:
            return
            
        existing_summary = conversation.summary or "No previous summary."
        
        # Formulate incremental prompt
        prompt = f"""
        You are summarizing a conversation.
        
        Existing Summary:
        {existing_summary}
        
        New Messages:
        """
        for msg in new_messages:
            prompt += f"\n{msg.role}: {msg.content}"
            
        prompt += "\n\nProvide an updated, concise summary of the entire conversation incorporating the new messages."
        
        payload = PromptPayload(
            system_prompt="You are a helpful assistant that summarizes conversations.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            # Simple non-streaming call to LLM
            # Assuming stream returns chunks, we collect them
            aggregated_summary = ""
            async for chunk in self.llm_workflow.stream(payload):
                if chunk.content_delta:
                    aggregated_summary += chunk.content_delta
                    
            # 5. Save Summary (Optimistic Concurrency)
            conversation.summary = aggregated_summary
            conversation.summarized_up_to_message_id = target_message_id
            
            # Using update_versioned or direct update
            # The repository pattern will throw if expected_version doesn't match
            await self.conversation_service.update_summary(conversation, expected_version)
            
        except Exception as e:
            logger.error(f"Permanent failure during summarization: {str(e)}")
            # Real infrastructure would handle retry logic up to max_retries
