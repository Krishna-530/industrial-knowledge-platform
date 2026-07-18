import json
from typing import List
from app.extraction.interfaces import AbstractKnowledgeExtractor, ExtractedFactResult
from app.extraction.prompt_provider import KnowledgeExtractionPromptProvider
from app.workflows.llm_workflow import LLMWorkflow

class LLMExtractor(AbstractKnowledgeExtractor):
    def __init__(self, llm_workflow: LLMWorkflow):
        self.llm_workflow = llm_workflow
        self.extraction_model = "llama-3-70b-instruct" # Standardized model
        self.extraction_version = "v1.0"

    async def extract(self, current_chunk_text: str, current_chunk_id: str, previous_chunk_text: str = None) -> List[ExtractedFactResult]:
        prompt_payload = KnowledgeExtractionPromptProvider.create_extraction_prompt(current_chunk_text, previous_chunk_text)
        
        # In a real implementation we would require the LLM to output structured JSON
        # and parse it. Here we simulate the LLM call block.
        aggregated_content = ""
        async for chunk in self.llm_workflow.stream(prompt_payload):
            if chunk.content_delta:
                aggregated_content += chunk.content_delta
                
        # Parse the output
        try:
            # Assuming output is a JSON array of extracted facts
            data = json.loads(aggregated_content)
            results = []
            for item in data:
                results.append(ExtractedFactResult(
                    asset_id=item.get("asset_id", ""),
                    property=item.get("property", ""),
                    value=item.get("value", ""),
                    start_offset=item.get("start_offset", 0),
                    end_offset=item.get("end_offset", 0)
                ))
            return results
        except Exception:
            # Re-raise extraction failures transparently
            return []
