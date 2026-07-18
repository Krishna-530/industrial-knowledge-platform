import logging
from typing import Dict

logger = logging.getLogger(__name__)

class QueryRewriteService:
    """
    Normalizes, expands abbreviations, and corrects terminology before planning.
    """
    _ABBREVIATIONS: Dict[str, str] = {
        "maint": "maintenance",
        "temp": "temperature",
        "hyd": "hydraulic",
        "vib": "vibration"
    }
    
    _SYNONYMS: Dict[str, str] = {
        "overheating": "thermal failure",
        "broken": "failure",
        "shutdown": "failure"
    }

    @classmethod
    def rewrite(cls, query: str) -> str:
        words = query.lower().split()
        rewritten_words = []
        
        for w in words:
            w_clean = w.strip(",.!?")
            # 1. Expand abbreviations
            if w_clean in cls._ABBREVIATIONS:
                rewritten_words.append(cls._ABBREVIATIONS[w_clean])
                continue
            
            # 2. Resolve synonyms
            if w_clean in cls._SYNONYMS:
                rewritten_words.append(cls._SYNONYMS[w_clean])
                continue
                
            rewritten_words.append(w)
            
        rewritten = " ".join(rewritten_words)
        if rewritten != query.lower():
            logger.info(f"Query Rewritten: '{query}' -> '{rewritten}'")
        return rewritten
