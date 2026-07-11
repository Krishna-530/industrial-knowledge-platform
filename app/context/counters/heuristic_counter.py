from app.context.interfaces import AbstractTokenCounter

class HeuristicTokenCounter(AbstractTokenCounter):
    """
    A basic character-based token counter heuristic.
    For more accurate counts (e.g. for OpenAI), swap this with a Tiktoken implementation in Phase 7.
    Rule of thumb: 1 token ~= 4 English characters.
    """
    def count(self, text: str) -> int:
        if not text:
            return 0
        return len(text) // 4 + 1
