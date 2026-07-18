import logging

logger = logging.getLogger(__name__)

def is_mime_type_allowed(file_header: bytes, allowed_mimes: list[str]) -> bool:
    """
    Validates MIME type by checking magic bytes.
    Currently a simplified check, designed to be swapped with libmagic in the future.
    """
    if file_header.startswith(b"%PDF-"):
        mime = "application/pdf"
    elif file_header.startswith(b"PK\x03\x04"):
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        # Fallback for text files or others without clear magic bytes.
        # In a real libmagic implementation, this would be robust.
        mime = "text/plain" 
        
    return mime in allowed_mimes
