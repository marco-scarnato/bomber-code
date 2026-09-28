import os
import requests

class CLMClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get("CLM_API_URL", "http://localhost:8700")

    def health(self):
        """Check the health status of the CLM API."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def system_one(self, state, questions, model="clm-latest", temperature=1.0):
        """
        Send state and questions to CLM /v1/systemone endpoint following TypeSafe wire format.
        """
        try:
            payload = {
                "state": state,
                "questions": questions,
                "model": model,
                "temperature": temperature
            }
            response = requests.post(f"{self.base_url}/v1/systemone", json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"CLM API request failed: {str(e)}")

    def rank(self, context, question, answers, model="clm-latest"):
        """
        Rank candidate answers given context and question.
        """
        try:
            payload = {
                "context": context,
                "question": question,
                "answers": answers,
                "model": model
            }
            response = requests.post(f"{self.base_url}/v1/rank", json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"CLM rank request failed: {str(e)}")