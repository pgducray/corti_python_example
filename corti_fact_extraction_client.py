import requests
from typing import Dict
from corti_client import CortiClient


class CortiFactExtractionClient(CortiClient):
    """
    Corti Fact Extraction API client for extracting structured medical facts from text.

    This class handles:
    - Extracting medical facts from clinical text
    - Processing referral letters, consultation notes, etc.
    """

    def extract_facts(self, text: str, output_language: str = "en-US") -> Dict:
        """
        Extract structured facts from medical text using Corti AI.

        Args:
            text: The medical text to analyze (e.g., referral letter, consultation notes)
            output_language: Language code for the output (default: "en-US")

        Returns:
            Dictionary containing:
            - facts: List of extracted medical facts
            - usageInfo: Information about credits consumed

        Example:
            >>> client = CortiFactExtractionClient()
            >>> result = client.extract_facts("Patient has chronic knee pain...")
            >>> print(result['facts'])
            >>> print(f"Credits used: {result['usageInfo']['creditsConsumed']}")
        """
        headers = self.get_headers(include_tenant=True)
        headers["Content-Type"] = "application/json"

        payload = {
            "context": [
                {
                    "type": "text",
                    "text": text
                }
            ],
            "outputLanguage": output_language
        }

        response = requests.post(
            f"{self.api_url}/tools/extract-facts",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
