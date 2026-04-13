# Corti Python API Client

Python client and Streamlit GUI for Corti's audio transcription and medical fact extraction APIs.

## Setup

### Option 1: Docker (Recommended)

```bash
# Configure credentials
cp .env-example .env
# Edit .env with your Corti API credentials

# Start application
docker-compose up -d

# Access at http://localhost:8501
```

### Option 2: Local Python

```bash
# Configure credentials
cp .env-example .env

# Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run application
streamlit run app/streamlit_app.py

# Access at http://localhost:8501
```

## Configuration

Edit `.env` with your credentials:

```env
CORTI_TENANT_NAME=your-tenant
CORTI_CLIENT_ID=your-client-id
CORTI_CLIENT_SECRET=your-secret
CORTI_ENVIRONMENT=eu
```

## Usage

### GUI (Streamlit)
- **Transcription Tab**: Upload audio files, configure options, view/download transcripts
- **Fact Extraction Tab**: Process medical text, extract structured facts
- **Results Browser**: View and download historical results

## Project Structure

```
src/                    # API clients
app/                    # Streamlit GUI
data/samples/           # Input samples
data/transcripts/       # Transcript outputs
data/facts/             # Fact extraction outputs
tests/                  # Test scripts
```

## Testing

```bash
python tests/test_transcript.py
python tests/test_detailed.py
```

## Docker Commands

```bash
docker-compose up -d      # Start
docker-compose logs -f    # View logs
docker-compose down       # Stop
```
