from repository_knowledge_assistant.utils import BaseIndex
from dataclasses import dataclass
from typing import List

@dataclass
class Interaction:
    question: str
    answer: str
    timestamp: str
    session_id: str
    message_id: str
    retrieved_documents: List[dict]


class InteractionIndex(BaseIndex):

    index_name: str
    mappings: dict = {
        "properties": {
            "question": {"type": "text"},
            "answer": {"type": "text"},
            "timestamp": {"type": "date"},
            "session_id": {"type": "keyword"},
            "message_id": {"type": "keyword"},
            "retrieved_documents": {
                "type": "nested",
                "properties": {
                    "file": {"type": "keyword"},
                    "chunk_id": {"type": "keyword"},
                    "score": {"type": "float"}
                }
            }
        }
    }

    def index_interaction(self, interaction: Interaction):
        self.client.index(
            index = self.index_name,
            id = f"{interaction.session_id}_{interaction.message_id}",
            document = {
                "question": interaction.question,
                "answer": interaction.answer,
                "timestamp": interaction.timestamp,
                "session_id": interaction.session_id,
                "message_id": interaction.message_id,
                "retrieved_documents": interaction.retrieved_documents
            }
        )