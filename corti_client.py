import requests
import os
import uuid
import time
from typing import Optional, Dict, List, BinaryIO

class CortiClient:
    def __init__(self):
        """Initialize the CortiClient by pulling credentials from the environment."""
        self.tenant_name = os.getenv("CORTI_TENANT_NAME")
        self.client_id = os.getenv("CORTI_CLIENT_ID")
        self.client_secret = os.getenv("CORTI_CLIENT_SECRET")
        self.environment = os.getenv("CORTI_ENVIRONMENT", "eu")

        # Auth URL - Corti uses Keycloak with realm pattern
        self.auth_url = f"https://auth.{self.environment}.corti.app/realms/{self.tenant_name}/protocol/openid-connect/token"
        # Fallback auth URL patterns (older formats)
        self.fallback_auth_urls = [
            f"https://auth.{self.environment}.corti.app/oauth2/token",
            f"https://{self.tenant_name}.{self.environment}.auth.corti.app/oauth2/token"
        ]

        # API URL - Corti uses api.{environment}.corti.app/v2
        self.api_url = f"https://api.{self.environment}.corti.app/v2"

        self.access_token: Optional[str] = None

    def is_configured(self) -> bool:
        """Check if all required credentials are present."""
        return bool(self.tenant_name and self.client_id and self.client_secret)

    def authenticate(self) -> str:
        """
        Authenticate via Client Credentials flow.
        Returns the access token and caches it.
        """
        if not self.is_configured():
            raise ValueError("Credentials missing. Check your .env file.")

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": "capioswe"
        }

        # Try primary auth URL
        last_error = None
        try:
            response = requests.post(self.auth_url, data=payload, timeout=10)
            response.raise_for_status()
            self.access_token = response.json().get("access_token")
            return self.access_token
        except requests.exceptions.RequestException as e:
            last_error = e

        # Try all fallback URLs
        for fallback_url in self.fallback_auth_urls:
            try:
                response = requests.post(fallback_url, data=payload, timeout=10)
                response.raise_for_status()
                self.access_token = response.json().get("access_token")
                return self.access_token
            except requests.exceptions.RequestException as e:
                last_error = e
                continue

        # All attempts failed
        raise Exception(
            f"Failed to authenticate using all available auth URLs. "
            f"Last error: {last_error}"
        )

    def get_headers(self) -> Dict[str, str]:
        """Return the headers required for API calls."""
        if not self.access_token:
            self.authenticate()
        return {"Authorization": f"Bearer {self.access_token}"}

    def list_agents(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """
        Fetch list of agents from Corti API.

        Args:
            limit: Maximum number of agents to return
            offset: Pagination offset

        Returns:
            List of agent dictionaries
        """
        headers = self.get_headers()
        response = requests.get(
            f"{self.api_url}/agents",
            headers=headers,
            params={"limit": limit, "offset": offset},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # Handle both list response and object with agents array
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'agents' in data:
            return data['agents']
        else:
            return []

    def get_agent_details(self, agent_id: str) -> Dict:
        """
        Get specific agent details by ID.

        Args:
            agent_id: The agent's unique identifier

        Returns:
            Agent details dictionary
        """
        headers = self.get_headers()
        response = requests.get(
            f"{self.api_url}/agents/{agent_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    # ========================================================================
    # TRANSCRIPTION METHODS (Phase 2)
    # ========================================================================

    def create_interaction(self) -> Dict:
        """
        Create a new interaction for transcription session.

        Returns:
            Interaction object containing interactionId
        """
        headers = self.get_headers()
        payload = {
            "encounter": {
                "identifier": str(uuid.uuid4()),
                "status": "planned",
                "type": "first_consultation"
            },
            "patient": {
                "identifier": str(uuid.uuid4()),
                "gender": "unknown"
            }
        }

        response = requests.post(
            f"{self.api_url}/interactions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def upload_recording(self, file: BinaryIO, interaction_id: str) -> Dict:
        """
        Upload MP3 file to Corti for transcription.

        Args:
            file: File-like object (from st.file_uploader or open())
            interaction_id: ID of the interaction created earlier

        Returns:
            Upload response containing recordingId
        """
        headers = self.get_headers()
        # Remove Content-Type to let requests set it with boundary for multipart
        headers_copy = {k: v for k, v in headers.items() if k.lower() != 'content-type'}

        files = {'file': file}

        response = requests.post(
            f"{self.api_url}/interactions/{interaction_id}/recordings",
            headers=headers_copy,
            files=files,
            timeout=120  # Longer timeout for file upload
        )
        response.raise_for_status()
        return response.json()

    def create_transcript(self, interaction_id: str, recording_id: str,
                         primary_language: str = "en") -> Dict:
        """
        Create transcript from an uploaded recording.

        Args:
            interaction_id: ID of the interaction
            recording_id: ID of the uploaded recording
            primary_language: Language code (default: "en")

        Returns:
            Transcript creation response containing transcript id
        """
        headers = self.get_headers()
        payload = {
            "recordingId": recording_id,
            "primaryLanguage": primary_language
        }

        response = requests.post(
            f"{self.api_url}/interactions/{interaction_id}/transcripts",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_transcript_status(self, interaction_id: str, transcript_id: str) -> Dict:
        """
        Check the status of a transcript (processing/completed/failed).

        Args:
            interaction_id: ID of the interaction
            transcript_id: ID of the transcript

        Returns:
            Status object with status field
        """
        headers = self.get_headers()
        response = requests.get(
            f"{self.api_url}/interactions/{interaction_id}/transcripts/{transcript_id}/status",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def get_transcript(self, interaction_id: str, transcript_id: str) -> Dict:
        """
        Get the final transcript results.

        Args:
            interaction_id: ID of the interaction
            transcript_id: ID of the transcript

        Returns:
            Complete transcript with segments, text, and metadata
        """
        headers = self.get_headers()
        response = requests.get(
            f"{self.api_url}/interactions/{interaction_id}/transcripts/{transcript_id}",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def wait_for_transcript(self, interaction_id: str, transcript_id: str,
                          max_wait_seconds: int = 300, poll_interval: int = 2) -> Dict:
        """
        Poll for transcript completion with timeout.

        Args:
            interaction_id: ID of the interaction
            transcript_id: ID of the transcript
            max_wait_seconds: Maximum time to wait in seconds (default: 5 minutes)
            poll_interval: Seconds between status checks (default: 2)

        Returns:
            Final transcript when completed

        Raises:
            TimeoutError: If transcript doesn't complete within max_wait_seconds
            Exception: If transcript processing fails
        """
        start_time = time.time()

        while time.time() - start_time < max_wait_seconds:
            status_response = self.get_transcript_status(interaction_id, transcript_id)
            status = status_response.get('status', 'processing')

            if status == 'completed':
                return self.get_transcript(interaction_id, transcript_id)
            elif status == 'failed':
                error_msg = status_response.get('error', 'Unknown error')
                raise Exception(f"Transcript processing failed: {error_msg}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Transcript did not complete within {max_wait_seconds} seconds")

    def delete_transcript(self, interaction_id: str, transcript_id: str) -> None:
        """Delete a transcript."""
        headers = self.get_headers()
        response = requests.delete(
            f"{self.api_url}/interactions/{interaction_id}/transcripts/{transcript_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

    def delete_recording(self, interaction_id: str, recording_id: str) -> None:
        """Delete a recording."""
        headers = self.get_headers()
        response = requests.delete(
            f"{self.api_url}/interactions/{interaction_id}/recordings/{recording_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

    def delete_interaction(self, interaction_id: str) -> None:
        """Delete an interaction."""
        headers = self.get_headers()
        response = requests.delete(
            f"{self.api_url}/interactions/{interaction_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

    # ========================================================================
    # FACT EXTRACTION METHODS
    # ========================================================================

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
            >>> client = CortiClient()
            >>> result = client.extract_facts("Patient has chronic knee pain...")
            >>> print(result['facts'])
            >>> print(f"Credits used: {result['usageInfo']['creditsConsumed']}")
        """
        headers = self.get_headers()
        # Add required Tenant-Name header per official API documentation
        headers["Tenant-Name"] = self.tenant_name
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
