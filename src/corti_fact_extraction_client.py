import requests
import os
import json
from typing import Dict
from .corti_client import CortiClient


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

    def save_facts(self, facts_result: Dict, file_name: str, output_format: str = "json") -> str:
        """
        Save extracted facts to a file.

        Args:
            facts_result: Complete API response with facts and usage info
            file_name: Name for the output file (without extension)
            output_format: "json" or "txt" (default: "json")

        Returns:
            Path to the saved file

        Example:
            >>> client = CortiFactExtractionClient()
            >>> result = client.extract_facts("Patient has chronic knee pain...")
            >>> file_path = client.save_facts(result, "knee_pain_analysis", "json")
            >>> print(f"Saved to: {file_path}")
        """
        folder_name = "data/facts"

        # Create folder if it doesn't exist
        os.makedirs(folder_name, exist_ok=True)

        # Add appropriate extension
        file_name_with_ext = f"{file_name}.{output_format}"
        file_path = os.path.join(folder_name, file_name_with_ext)

        try:
            if output_format == "json":
                # Save complete JSON response
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(facts_result, f, indent=2, ensure_ascii=False)
                print(f"✅ Facts saved as JSON to: {file_path}")

            elif output_format == "txt":
                # Save readable text format
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("=" * 70 + "\n")
                    f.write("CORTI FACT EXTRACTION RESULTS\n")
                    f.write("=" * 70 + "\n\n")

                    # Write usage info
                    if 'usageInfo' in facts_result:
                        credits = facts_result['usageInfo'].get('creditsConsumed', 'N/A')
                        f.write(f"Credits Consumed: {credits}\n\n")

                    # Write facts
                    if 'facts' in facts_result:
                        facts = facts_result['facts']
                        f.write(f"Extracted Facts ({len(facts)} total):\n")
                        f.write("-" * 70 + "\n\n")

                        for i, fact in enumerate(facts, 1):
                            f.write(f"{i}. {fact}\n\n")
                    else:
                        f.write("No facts extracted.\n")

                    f.write("\n" + "=" * 70 + "\n")

                print(f"✅ Facts saved as text to: {file_path}")
            else:
                raise ValueError(f"Unsupported format: {output_format}. Use 'json' or 'txt'")

            return file_path

        except Exception as e:
            print(f"❌ An error occurred while saving facts: {e}")
            raise
