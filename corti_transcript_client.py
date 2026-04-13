import requests
import uuid
import time
from typing import Optional, Dict, List, BinaryIO
from corti_client import CortiClient


class CortiTranscriptClient(CortiClient):
    """
    Corti Transcript API client for single-file transcription workflows.

    Workflow for transcribing a single audio file:
    1. Create interaction → get interaction_id
    2. Upload recording → get recording_id
    3. Create transcript with options (diarization, multi-channel, etc.)
    4. Poll status until completion
    5. Get final transcript results

    This class provides the 5 core transcript API endpoints:
    - list_transcripts() - List all transcripts for an interaction
    - create_transcript() - Create a new transcript
    - get_transcript() - Get transcript content
    - get_transcript_status() - Check processing status
    - delete_transcript() - Remove a transcript

    Plus supporting methods for the complete workflow:
    - create_interaction(), upload_recording(), wait_for_transcript()
    - delete_interaction(), delete_recording()
    """

    def create_interaction(self) -> Dict:
        """
        Create a new interaction for transcription session.

        Returns:
            Interaction object containing interactionId
        """
        headers = self.get_headers(include_tenant=True)
        headers["Content-Type"] = "application/json"
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
        Upload audio file to Corti for transcription.

        Args:
            file: File-like object (from open())
            interaction_id: ID of the interaction created earlier

        Returns:
            Upload response containing recordingId
        """
        headers = self.get_headers(include_tenant=True)
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

    def create_transcript(
        self,
        interaction_id: str,
        recording_id: str,
        primary_language: str = "en",
        is_dictation: bool = False,
        is_multichannel: bool = False,
        diarize: bool = False,
        participants: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Create transcript from an uploaded recording.

        Args:
            interaction_id: ID of the interaction
            recording_id: ID of the uploaded recording
            primary_language: Language code (default: "en")
            is_dictation: Whether the recording is dictation (default: False)
            is_multichannel: Whether the recording has multiple channels (default: False)
            diarize: Whether to perform speaker diarization (default: False)
            participants: List of participant objects with channel and role info
                         Example: [{"channel": 1, "role": "doctor"}]

        Returns:
            Transcript creation response containing transcript id

        Example:
            >>> client = CortiTranscriptClient()
            >>> result = client.create_transcript(
            ...     interaction_id="abc123",
            ...     recording_id="rec456",
            ...     primary_language="en",
            ...     is_multichannel=True,
            ...     diarize=True,
            ...     participants=[{"channel": 1, "role": "doctor"}]
            ... )
        """
        headers = self.get_headers(include_tenant=True)
        headers["Content-Type"] = "application/json"

        payload = {
            "recordingId": recording_id,
            "primaryLanguage": primary_language,
            "isDictation": is_dictation,
            "isMultichannel": is_multichannel,
            "diarize": diarize
        }

        # Add participants if provided
        if participants:
            payload["participants"] = participants

        response = requests.post(
            f"{self.api_url}/interactions/{interaction_id}/transcripts",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def list_transcripts(self, interaction_id: str) -> List[Dict]:
        """
        List all transcripts for a given interaction.

        Args:
            interaction_id: ID of the interaction

        Returns:
            List of transcript objects
        """
        headers = self.get_headers(include_tenant=True)
        response = requests.get(
            f"{self.api_url}/interactions/{interaction_id}/transcripts",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # Handle both list response and object with transcripts array
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'transcripts' in data:
            return data['transcripts']
        else:
            return []

    def get_transcript_status(self, interaction_id: str, transcript_id: str) -> Dict:
        """
        Check the status of a transcript (processing/completed/failed).

        Args:
            interaction_id: ID of the interaction
            transcript_id: ID of the transcript

        Returns:
            Status object with status field
        """
        headers = self.get_headers(include_tenant=True)
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
        headers = self.get_headers(include_tenant=True)
        response = requests.get(
            f"{self.api_url}/interactions/{interaction_id}/transcripts/{transcript_id}",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def delete_transcript(self, interaction_id: str, transcript_id: str) -> None:
        """
        Delete a transcript.

        Args:
            interaction_id: ID of the interaction
            transcript_id: ID of the transcript
        """
        headers = self.get_headers(include_tenant=True)
        response = requests.delete(
            f"{self.api_url}/interactions/{interaction_id}/transcripts/{transcript_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

    def wait_for_transcript(
        self,
        interaction_id: str,
        transcript_id: str,
        max_wait_seconds: int = 300,
        poll_interval: int = 2
    ) -> Dict:
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

    def save_transcription_text(self, transcript: Dict, file_name: str) -> None:
        """
        Save the full transcript text to a file.

        Args:
            transcript: Transcript object containing 'text' field
            file_name: Name to save the transcript text file
        """

        # Initialize as a list for better performance
        transcript_parts = []

        if 'transcripts' in transcript:
            for entry in transcript['transcripts']:
                # Check if the key exists and matches the channel
                if entry.get('channel') == 1 and 'text' in entry:
                    transcript_parts.append(entry['text'])

        # Join the list into a single string separated by a space (or newline)
        transcript_text = " ".join(transcript_parts)

        folder_name = "transcripts_text"
        file_path = folder_name + file_name

        # Write the transcript_text to the file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            print(f"✅ Transcript successfully saved to: {file_path}")
        except Exception as e:
            print(f"❌ An error occurred while saving transcript: {e}")

    def delete_recording(self, interaction_id: str, recording_id: str) -> None:
        """
        Delete a recording.

        Args:
            interaction_id: ID of the interaction
            recording_id: ID of the recording
        """
        headers = self.get_headers(include_tenant=True)
        response = requests.delete(
            f"{self.api_url}/interactions/{interaction_id}/recordings/{recording_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

    def delete_interaction(self, interaction_id: str) -> None:
        """
        Delete an interaction.

        Args:
            interaction_id: ID of the interaction
        """
        headers = self.get_headers(include_tenant=True)
        response = requests.delete(
            f"{self.api_url}/interactions/{interaction_id}",
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
