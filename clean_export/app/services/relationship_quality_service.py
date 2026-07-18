class RelationshipQualityService:
    """
    Computes a deterministic Quality Score for relationships to prevent graph oscillation 
    and provide mathematical confidence beyond raw LLM probability.
    """
    
    @staticmethod
    def calculate_score(base_confidence: float, evidence_count: int, provider_reliability_weight: float = 1.0) -> float:
        """
        Quality Score = (Base Confidence * 0.4) + (Evidence Count Bonus) + (Provider Reliability)
        
        We scale up quality linearly as more evidence chunks corroborate the same edge.
        """
        # Ensure base confidence is sane
        base_confidence = max(0.0, min(1.0, base_confidence))
        
        # Base weight (40%)
        weighted_base = base_confidence * 0.4
        
        # Evidence Bonus: +0.1 per additional piece of evidence, capped at +0.4 (4 pieces)
        evidence_bonus = min(0.4, max(0.0, (evidence_count - 1) * 0.1))
        
        # Provider Reliability (20% for top tier)
        provider_bonus = provider_reliability_weight * 0.2
        
        total_score = weighted_base + evidence_bonus + provider_bonus
        
        # Cap at 1.0
        return min(1.0, total_score)
