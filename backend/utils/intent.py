
from typing import Tuple


class IntentClassifier:
    """
    A simple rule-based intent classifier for CivicNavigator.
    Returns an (intent, confidence) tuple.
    """

    def __init__(self) -> None:
        # Keyword groups for different intents
        self.incident_keywords = [
            "report", "issue", "problem", "broken", "damaged",
            "pothole", "graffiti", "complaint", "leak", "streetlight"
        ]
        self.status_keywords = [
            "status", "check", "update", "progress", "resolved",
            "done", "fixed", "pending"
        ]
        self.query_keywords = [
            "how", "where", "what", "when", "who", "why",
            "information", "details", "process", "apply"
        ]

    async def classify_intent(self, message: str) -> Tuple[str, float]:
        """
        Classify the intent of a user message.

        Args:
            message (str): The user input message.

        Returns:
            Tuple[str, float]: (intent, confidence score)
        """
        message_lower = message.lower()

        if any(word in message_lower for word in self.incident_keywords):
            return "incident_report", 0.95

        elif any(word in message_lower for word in self.status_keywords):
            return "status_check", 0.95

        elif any(word in message_lower for word in self.query_keywords):
            return "general_query", 0.90

        return "unknown", 0.50
