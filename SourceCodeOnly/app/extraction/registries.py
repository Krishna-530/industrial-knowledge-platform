import enum

class PredicateRegistry(str, enum.Enum):
    """
    Canonical taxonomy for relationships. 
    Prevents LLMs from inventing unpredictable predicates.
    """
    # Structural
    PART_OF = "PART_OF"
    CONTAINS = "CONTAINS"
    LOCATED_IN = "LOCATED_IN"
    INSTALLED_ON = "INSTALLED_ON"
    
    # Operational/Causal
    CAUSES = "CAUSES"
    FAILS_BEFORE = "FAILS_BEFORE"
    FAILS_AFTER = "FAILS_AFTER"
    PRODUCES = "PRODUCES"
    CONSUMES = "CONSUMES"
    GENERATES = "GENERATES"
    
    # Organizational
    OWNS = "OWNS"
    OPERATED_BY = "OPERATED_BY"
    SUPPLIED_BY = "SUPPLIED_BY"
    MANUFACTURED_BY = "MANUFACTURED_BY"
    
    # Semantic
    MENTIONS = "MENTIONS"
    DESCRIBES = "DESCRIBES"
    RELATED_TO = "RELATED_TO"
    
    @classmethod
    def from_synonym(cls, synonym: str) -> "PredicateRegistry":
        synonym = synonym.upper()
        mapping = {
            "HAS_COMPONENT": cls.CONTAINS,
            "INCLUDES": cls.CONTAINS,
            "HAS": cls.CONTAINS,
            "IS_LOCATED_IN": cls.LOCATED_IN,
            "WORKS_WITH": cls.RELATED_TO,
            "USES": cls.CONSUMES,
            "OPERATES_WITH": cls.CONSUMES
        }
        return mapping.get(synonym, cls.RELATED_TO) # Fallback to RELATED_TO if unknown but enforced by Pydantic anyway
