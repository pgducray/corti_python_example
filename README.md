# Corti Python API Client 🏥

A comprehensive Python client library and Streamlit GUI for Corti's API, supporting audio transcription and medical fact extraction.

## 🌟 Features

- ✅ **Authentication** - OAuth2 Client Credentials flow with automatic token management
- 🎙️ **Audio Transcription** - Upload and transcribe audio files with advanced features (diarization, multi-channel)
- 🔬 **Fact Extraction** - Extract structured medical facts from clinical text
- �️ **Streamlit GUI** - User-friendly web interface for non-technical users
- 🐳 **Docker Support** - Easy deployment with Docker and Docker Compose
- �📦 **Modular Design** - Separate clients for different API services

## 📁 Project Structure

```
corti_python_example/
├── src/                          # Core API clients
│   ├── __init__.py
│   ├── corti_client.py          # Base authentication client
│   ├── corti_transcript_client.py    # Transcription client
│   └── corti_fact_extraction_client.py    # Fact extraction client
│
├── app/                          # Streamlit GUI application
│   └── streamlit_app.py         # Main web interface
│
├── data/                         # Data storage
│   ├── samples/                  # Input samples
│   ├── transcripts/              # Transcript outputs
│   └── facts/                    # Fact extraction outputs
│
├── tests/                        # Test scripts
│   ├── test_transcript.py
│   └── test_detailed.py
│
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose orchestration
├── requirements.txt              # Python dependencies
├── .env-example                  # Environment variables template
└── README.md                     # This file
```

## 🚀 Quick Start

### Option 1: Local Installation

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd corti_python_example
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure credentials**
   ```bash
   cp .env-example .env
   # Edit .env with your Corti API credentials
   ```

5. **Run Streamlit GUI**
   ```bash
   streamlit run app/streamlit_app.py
   ```

   The app will open at `http://localhost:8501`

### Option 2: Docker Deployment (Recommended)

1. **Configure credentials**
   ```bash
   cp .env-example .env
   # Edit .env with your Corti API credentials
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**

   Open your browser to `http://localhost:8501`

4. **View logs**
   ```bash
   docker-compose logs -f
   ```

5. **Stop the application**
   ```bash
   docker-compose down
   ```

## ⚙️ Configuration

Create a `.env` file with your Corti API credentials:

```env
CORTI_TENANT_NAME=your-tenant
CORTI_CLIENT_ID=your-client-id
CORTI_CLIENT_SECRET=your-secret
CORTI_ENVIRONMENT=eu
```

## 🖥️ Streamlit GUI

The Streamlit interface provides three main sections:

### 🎙️ Transcription Tab
- Upload audio files or select from samples
- Configure transcription options:
  - Language selection
  - Multi-channel support
  - Speaker diarization
  - Dictation mode
- Real-time processing status
- View and download transcripts

### 🔬 Fact Extraction Tab
- Upload text files, paste text, or use samples
- Select output language
- Choose save format (JSON or TXT)
- View extracted facts
- Download results

### 📂 Results Browser
- Browse historical transcriptions
- View previous fact extractions
- Download previous results
- File metadata display

## 💻 Programmatic Usage

### Transcription Example

```python
from src.corti_transcript_client import CortiTranscriptClient
from dotenv import load_dotenv

load_dotenv()

client = CortiTranscriptClient()

# Create interaction
interaction = client.create_interaction()
interaction_id = interaction['interactionId']

# Upload audio
with open('audio.mp3', 'rb') as f:
    upload = client.upload_recording(f, interaction_id)
    recording_id = upload['recordingId']

# Create transcript with options
transcript_response = client.create_transcript(
    interaction_id=interaction_id,
    recording_id=recording_id,
    primary_language="en",
    is_multichannel=True,
    diarize=True,
    participants=[{"channel": 1, "role": "doctor"}]
)

# Wait for completion
transcript = client.wait_for_transcript(
    interaction_id=interaction_id,
    transcript_id=transcript_response['transcriptId'],
    max_wait_seconds=300
)

print(transcript['text'])

# Cleanup
client.delete_transcript(interaction_id, transcript_response['transcriptId'])
client.delete_recording(interaction_id, recording_id)
client.delete_interaction(interaction_id)
```

### Fact Extraction Example

```python
from src.corti_fact_extraction_client import CortiFactExtractionClient
from dotenv import load_dotenv

load_dotenv()

client = CortiFactExtractionClient()

# Extract facts
medical_text = "Patient has chronic knee pain with limited mobility..."
result = client.extract_facts(medical_text, output_language="en-US")

# Display results
print(f"Facts: {result['facts']}")
print(f"Credits used: {result['usageInfo']['creditsConsumed']}")

# Save results
client.save_facts(result, "patient_analysis", output_format="json")
```

## 🧪 Testing

Run the test scripts to verify your setup:

### Test Transcription
```bash
python tests/test_transcript.py
```

### Test Fact Extraction
```bash
python tests/test_detailed.py
```

## 📚 API Clients

### CortiClient (Base)
Core authentication and configuration:
- OAuth2 authentication with multiple auth URL fallback
- Environment configuration (EU, US, etc.)
- Shared header generation

### CortiTranscriptClient
Complete transcription workflow:
- `create_interaction()` - Create interaction session
- `upload_recording()` - Upload audio files
- `create_transcript()` - Create transcript with options
- `list_transcripts()` - List all transcripts
- `get_transcript_status()` - Check processing status
- `get_transcript()` - Retrieve completed transcript
- `wait_for_transcript()` - Poll until completion
- `save_transcription_text()` - Save to file
- `delete_transcript()`, `delete_recording()`, `delete_interaction()` - Cleanup

### CortiFactExtractionClient
Medical fact extraction:
- `extract_facts()` - Extract structured medical facts
- `save_facts()` - Save results in JSON or TXT format

## 🐳 Docker Details

### Building the Image
```bash
docker build -t corti-app .
```

### Running with Custom Port
```bash
docker run -p 8080:8501 --env-file .env corti-app
```

### Volume Mounts
The Docker Compose setup mounts:
- `./data:/app/data` - Data persistence
- `./src:/app/src` - Source code (for development)
- `./app:/app/app` - Streamlit app (for development)

## 📊 Data Management

### Input Samples
Place sample files in `data/samples/`:
- Audio files: `.mp3`, `.wav`, `.ogg`, `.flac`, `.m4a`
- Text files: `.txt`, `.md`

### Output Data
- Transcripts saved to: `data/transcripts/`
- Fact extractions saved to: `data/facts/`

## 🔒 Security

- Non-root user in Docker container
- Environment variables for sensitive credentials
- `.env` file excluded from version control
- Health checks for container monitoring

## 🛠️ Development

### Running Locally for Development
```bash
# Install in development mode
pip install -e .

# Run Streamlit with auto-reload
streamlit run app/streamlit_app.py --server.runOnSave=true
```

### Code Structure
- `src/` - Pure API client logic (no UI dependencies)
- `app/` - Streamlit interface (imports from src)
- `tests/` - Test scripts demonstrating usage

## 📋 Requirements

- Python 3.7+
- Docker & Docker Compose (for containerized deployment)

### Python Dependencies
- `requests>=2.31.0` - HTTP client
- `python-dotenv>=1.0.0` - Environment management
- `streamlit>=1.31.0` - Web interface

## 🤝 Contributing

When adding new features:
1. Add client methods to appropriate `src/` module
2. Update Streamlit GUI in `app/streamlit_app.py`
3. Add test scripts in `tests/`
4. Update this README

## 📝 Sample Files

The repository includes sample files in `data/samples/`:
- Orthopedic Referral Letter (text) - For fact extraction
- Patient consultation audio files - For transcription

## 🆘 Troubleshooting

### API Authentication Issues
- Verify credentials in `.env` file
- Check tenant name and environment setting
- Ensure client has proper permissions

### Docker Issues
```bash
# Rebuild without cache
docker-compose build --no-cache

# View logs
docker-compose logs -f corti-app

# Restart service
docker-compose restart
```

### Streamlit Issues
```bash
# Clear cache
streamlit cache clear

# Run with verbose logging
streamlit run app/streamlit_app.py --logger.level=debug
```

## 📄 License

[Your License Here]

## 🔗 Links

- [Corti API Documentation](https://docs.corti.ai/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

Built with ❤️ for Corti API integration | Powered by Streamlit
