from app.workflows.models.prompt_payload import PromptPayload

class KnowledgeExtractionPromptProvider:
    @staticmethod
    def create_extraction_prompt(current_chunk_text: str, previous_chunk_text: str = None) -> PromptPayload:
        context = ""
        if previous_chunk_text:
            context += f"Previous Chunk (for context only):\n{previous_chunk_text}\n\n"
        context += f"Current Chunk (Extract facts from here):\n{current_chunk_text}"
        
        system_prompt = (
            "You are an industrial knowledge extraction system. "
            "Extract structured facts (asset_id, property, value, start_offset, end_offset) "
            "from the Current Chunk. start_offset and end_offset must match the exact character offsets "
            "of the source quote within the Current Chunk. "
            "Return JSON matching the schema."
        )
        
        return PromptPayload(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": context}]
        )
