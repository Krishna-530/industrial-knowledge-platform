"""
In-memory token blacklist for Phase 2.
TODO: In Phase 3, this must be migrated to Redis to support multi-worker environments.
"""
token_blacklist: set[str] = set()

def add_to_blacklist(token: str) -> None:
    token_blacklist.add(token)

def is_blacklisted(token: str) -> bool:
    return token in token_blacklist
