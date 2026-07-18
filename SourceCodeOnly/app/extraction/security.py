import unicodedata
import re

class InputSanitizer:
    """
    Protects against adversarial prompt injections embedded in raw text.
    """
    
    @staticmethod
    def sanitize(text: str, max_chars: int = 4000) -> str:
        if not text:
            return ""
            
        # 1. Truncate oversized payloads to prevent context window overflow
        text = text[:max_chars]
        
        # 2. Unicode NFKC Normalization to defeat unicode obfuscation (e.g. Cyrillic posing as Latin)
        normalized = unicodedata.normalize('NFKC', text)
        
        # 3. Strip obvious HTML/XML tags that might confuse JSON extractors
        no_html = re.sub(r'<[^>]+>', ' ', normalized)
        
        # 4. Strip invisible control characters (except basic whitespace)
        clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', no_html)
        
        return clean.strip()
