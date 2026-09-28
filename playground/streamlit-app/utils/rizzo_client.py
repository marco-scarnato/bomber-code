import os
import requests

class RizzoClient:
    def __init__(self, base_url=None):
        # Default to environment variable or localhost
        self.base_url = base_url or os.environ.get("RIZZO_API_URL", "http://localhost:8017")

    def health(self):
        """Check the health status of the Rizzo-Flow API."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def decide(self, state, questions):
        """
        Send a state and questions to the Rizzo-Flow API for probabilistic decisions.
        Timeout is set to 60 seconds as CPU inference can be slow.
        """
        try:
            payload = {
                "state": state,
                "questions": questions
            }
            response = requests.post(f"{self.base_url}/v1/decisions", json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Rizzo-Flow API request failed: {str(e)}")
