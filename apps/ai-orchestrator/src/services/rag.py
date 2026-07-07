import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger("ai-orchestrator")

class RAGService:
    def __init__(self):
        # Simulated Vector Database embeddings storage
        self.kb_index = [
            {
                "id": "DOC-FIFA-SEC-01",
                "title": "FIFA Stadium Safety Standards 2026",
                "text": "Evacuation gates must remain completely clear of merchandise kiosks. If crowd occupancy exceeds 90% in Zone concourses, entry gates must transition to pulse-mode turnstile flows."
            },
            {
                "id": "DOC-FIFA-MED-04",
                "title": "Heat Stress Response Manual",
                "text": "For temperatures exceeding 85F (29C), emergency service agents must establish hydration cooling zones at every third concourse node. Volunteer coordinators are task-dispatched to distribute water bottles."
            },
            {
                "id": "DOC-STAD-OPS-03",
                "title": "StadiumOS Concession Rules",
                "text": "Concession inventory checks are executed automatically. If water bottle stock is below 100 units at any Vendor kiosk, operations trigger re-stock requests to concourse warehouse hubs."
            }
        ]

    def search_kb(self, query: str, threshold: float = 0.6) -> List[Dict[str, Any]]:
        logger.info(f"Executing Vector RAG search query: '{query}'")
        matches = []
        q_lower = query.lower()
        for doc in self.kb_index:
            if any(word in doc["text"].lower() or word in doc["title"].lower() for word in q_lower.split()):
                matches.append(doc)
        
        if not matches:
            matches = [self.kb_index[0]]
            
        return matches

    def build_context(self, matches: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
        context_str = "\n\n".join([f"Source: {d['title']} ({d['id']})\nContent: {d['text']}" for d in matches])
        citations = [f"{d['title']} ({d['id']})" for d in matches]
        return context_str, citations

# Singleton instance
rag_service = RAGService()
