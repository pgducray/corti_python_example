# Corti Python API Client

Python client library for Corti's API, supporting single-file transcription and fact extraction.

## Features

- ✅ **Authentication** - OAuth2 Client Credentials flow with automatic token management
- 🎙️ **Single-File Transcription** - Upload and transcribe audio files with advanced features (diarization, multi-channel)
- 🔬 **Fact Extraction** - Extract structured medical facts from clinical text
- 📦 **Modular Design** - Separate clients for different API services

## Architecture

The library is organized into three separate client modules:

### 1. `corti_client.py` - Base Client
Core authentication and configuration:
- OAuth2 authentication with multiple auth URL fallback
- Environment configuration (EU, US, etc.)
- Shared header generation

### 2. `corti_transcript_client.py` - Transcription Client
Complete transcription workflow management:
- `create_interaction()` - Create interaction session
- `upload_recording()` - Upload audio files (MP3, WAV, etc.)
- `create_transcript()` - Create transcript with advanced options:
  - Speaker diarization
  - Multi-channel support
  - Participant role assignment
  - Dictation mode
- `list_transcripts()` - List all transcripts for an interaction
- `get_transcript_status()` - Check processing status
- `get_transcript()` - Retrieve completed transcript
- `wait_for_transcript()` - Poll until completion
- `save_transcription_text()` - Save transcript to text file
- `delete_transcript()`, `delete_recording()`, `delete_interaction()` - Cleanup methods

### 3. `corti_fact_extraction_client.py` - Fact Extraction Client
Medical fact extraction from text:
- `extract_facts()` - Extract structured medical facts from clinical text

## Setup

```bash
pip install -r requirements.txt
```

Copy `.env-example` to `.env` and add your credentials:

```
CORTI_TENANT_NAME=your-tenant
CORTI_CLIENT_ID=your-client-id
CORTI_CLIENT_SECRET=your-secret
CORTI_ENVIRONMENT=eu
```

## Usage Examples

### Fact Extraction

```python
from corti_fact_extraction_client import CortiFactExtractionClient

client = CortiFactExtractionClient()

# Extract facts from medical text
result = client.extract_facts(
    text="Patient has chronic knee pain with limited mobility...",
    output_language="en-US"
)

print(f"Facts: {result['facts']}")
print(f"Credits used: {result['usageInfo']['creditsConsumed']}")
```

### Transcription with Advanced Features

```python
from corti_transcript_client import CortiTranscriptClient

client = CortiTranscriptClient()

# Step 1: Create interaction
interaction = client.create_interaction()
interaction_id = interaction['interactionId']

# Step 2: Upload recording
with open('consultation.mp3', 'rb') as f:
    upload = client.upload_recording(f, interaction_id)
    recording_id = upload['recordingId']

# Step 3: Create transcript with advanced options
transcript_response = client.create_transcript(
    interaction_id=interaction_id,
    recording_id=recording_id,
    primary_language="en",
    is_dictation=False,
    is_multichannel=True,
    diarize=True,  # Enable speaker diarization
    participants=[
        {"channel": 1, "role": "doctor"},
        {"channel": 2, "role": "patient"}
    ]
)

transcript_id = transcript_response['transcriptId']

# Step 4: Wait for completion
transcript = client.wait_for_transcript(
    interaction_id=interaction_id,
    transcript_id=transcript_id,
    max_wait_seconds=300
)

print(f"Transcript: {transcript['text']}")
print(f"Segments: {transcript['segments']}")

# Step 5: Save transcript to file
client.save_transcription_text(
    transcript=transcript,
    file_name="consultation_transcript.txt"
)

# Step 6: Cleanup
client.delete_transcript(interaction_id, transcript_id)
client.delete_recording(interaction_id, recording_id)
client.delete_interaction(interaction_id)
```

### List All Transcripts

```python
# Get all transcripts for an interaction
transcripts = client.list_transcripts(interaction_id)

for t in transcripts:
    print(f"Transcript ID: {t['transcriptId']}, Status: {t['status']}")
```

## Test Scripts

Run the included test scripts to verify your setup:

### Test Fact Extraction
```bash
python test_detailed.py
```
Extracts facts from the sample orthopedic referral letter.

### Test Transcription
```bash
python test_transcript.py
```
Complete transcription workflow test with advanced features (diarization, multi-channel).

## API Endpoints

### Transcription
```
POST https://api.{environment}.corti.app/v2/interactions/{id}/transcripts/
```

Payload with advanced options:
```json
{
  "recordingId": "uuid",
  "primaryLanguage": "en",
  "isDictation": false,
  "isMultichannel": true,
  "diarize": true,
  "participants": [
    {"channel": 1, "role": "doctor"}
  ]
}
```

### Fact Extraction
```
POST https://api.{environment}.corti.app/v2/tools/extract-facts
```

Payload:
```json
{
  "context": [{"type": "text", "text": "medical text..."}],
  "outputLanguage": "en-US"
}
```

## Sample Files

- `Sample/Orthopedic Referral Letter.txt` - Sample medical text for fact extraction
- `Sample/Patient Consultation with MI.mp3` - Sample audio for transcription
- `Sample/TalkCPR- A real patient and doctor interaction filmed.mp3` - Alternative audio sample

## Requirements

- Python 3.7+
- requests
- python-dotenv

---

Built for Corti API integration. Supports both transcription and fact extraction workflows.
