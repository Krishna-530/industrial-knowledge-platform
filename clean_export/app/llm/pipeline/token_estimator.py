from app.prompt.models.schemas import PromptPayload

class TokenEstimator:
    def estimate_tokens(self, payload: PromptPayload) -> int:
        """
        A heuristic token estimator (e.g., 1 token approx 4 characters).
        In a production environment this would use tiktoken or similar.
        """
        total_chars = 0
        for message in payload.messages:
            total_chars += len(message.content)
            
        return max(1, total_chars // 4)
