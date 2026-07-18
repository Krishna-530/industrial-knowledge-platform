import logging

def get_logger(name: str) -> logging.Logger:
    """Return a logger configured for the given name."""
    return logging.getLogger(name)
