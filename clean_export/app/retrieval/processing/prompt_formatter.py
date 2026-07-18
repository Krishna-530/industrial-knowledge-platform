from typing import List, Dict, Any

class GraphPromptFormatter:
    """
    Translates raw JSON edges into LLM-friendly syntax.
    Decoupled from budgeting to allow switching formats (Markdown, XML, JSON) easily.
    """
    
    @staticmethod
    def compress(edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compresses the graph context by collapsing repeated entity paths 
        before format serialization, retaining pure semantic meaning.
        """
        # Example: Node A -> Node B and Node A -> Node C becomes Node A -> [Node B, Node C]
        # For simplicity, returning edges as is in stub.
        return edges

    @staticmethod
    def format_as_markdown(edges: List[Dict[str, Any]]) -> str:
        compressed_edges = GraphPromptFormatter.compress(edges)
        lines = ["### Knowledge Graph Connections"]
        for edge in compressed_edges:
            sub = edge.get("subject_id", "Unknown")
            pred = edge.get("predicate", "RELATED_TO")
            obj = edge.get("object_id", "Unknown")
            
            prov = edge.get("provenance", {})
            doc = prov.get("document_id", "N/A")
            
            # Simple [Subject] --(PREDICATE)--> [Object]
            lines.append(f"- `[{sub}]` --({pred})--> `[{obj}]` (Source: {doc})")
            
        return "\n".join(lines)
        
    @staticmethod
    def format_as_xml(edges: List[Dict[str, Any]]) -> str:
        lines = ["<knowledge_graph>"]
        for edge in edges:
            sub = edge.get("subject_id", "Unknown")
            pred = edge.get("predicate", "RELATED_TO")
            obj = edge.get("object_id", "Unknown")
            lines.append(f"  <edge subject=\"{sub}\" predicate=\"{pred}\" object=\"{obj}\"/>")
        lines.append("</knowledge_graph>")
        return "\n".join(lines)
