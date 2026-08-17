from repository_knowledge_assistant.utils import BaseIndex
from dataclasses import dataclass


@dataclass
class Feedback:
    feedback: int
    timestamp: str
    session_id: str
    message_id: str


class FeedbackIndex(BaseIndex):

    index_name: str
    mappings: dict = {
        "properties": {
            "feedback": {"type": "integer"},
            "timestamp": {"type": "date"},
            "session_id": {"type": "keyword"},
            "message_id": {"type": "keyword"}
        }
    }

    def index_feedback(self, feedback: Feedback):
        self.client.index(
            index = self.index_name,
            id = f"{feedback.session_id}_{feedback.message_id}",
            document = {
                "feedback": feedback.feedback,
                "timestamp": feedback.timestamp,
                "session_id": feedback.session_id,
                "message_id": feedback.message_id
            }
        )