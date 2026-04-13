# 🚀 Quick Start Guide

## 30-Second Setup

### Option 1: Docker (Recommended)
```bash
# 1. Configure credentials
cp .env-example .env
# Edit .env with your Corti API credentials

# 2. Start the application
./run_docker.sh
# or
docker-compose up -d

# 3. Open browser
# http://localhost:8501
```

### Option 2: Local Python
```bash
# 1. Configure credentials
cp .env-example .env
# Edit .env with your Corti API credentials

# 2. Start the application
./run_streamlit.sh
# or manually:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## What's New? ✨

### Project Structure
- **`src/`** - Core API clients (modular, reusable)
- **`app/`** - Streamlit web interface
- **`data/`** - All input/output data organized
- **`tests/`** - Test scripts

### Features
1. **🖥️ Streamlit GUI** - User-friendly web interface
2. **🎙️ Transcription** - Upload audio or use samples
3. **🔬 Fact Extraction** - Process text with multiple input options
4. **📂 Results Browser** - View and download historical results
5. **🐳 Docker Ready** - One-command deployment
6. **💾 Auto-Save** - Results automatically saved to `data/`

### New `save_facts()` Method
```python
from src.corti_fact_extraction_client import CortiFactExtractionClient

client = CortiFactExtractionClient()
result = client.extract_facts("Medical text here...")

# Save in JSON or TXT format
client.save_facts(result, "output_name", output_format="json")
```

## Data Locations
- **Samples**: `data/samples/`
- **Transcripts**: `data/transcripts/`
- **Fact Extractions**: `data/facts/`

## Useful Commands

### Docker
```bash
docker-compose up -d          # Start
docker-compose logs -f        # View logs
docker-compose down           # Stop
docker-compose restart        # Restart
```

### Local Development
```bash
streamlit run app/streamlit_app.py        # Run GUI
python tests/test_transcript.py           # Test transcription
python tests/test_detailed.py             # Test fact extraction
```

## Troubleshooting

**Issue**: Cannot connect to API
- Check `.env` credentials are correct
- Verify `CORTI_ENVIRONMENT` is set (eu/us)

**Issue**: Docker port conflict
- Change port in `docker-compose.yml`: `"8080:8501"`

**Issue**: Module import errors
- For tests: Run from project root
- Ensure virtual environment is activated

## Next Steps

1. Add your audio/text samples to `data/samples/`
2. Open http://localhost:8501
3. Try the Transcription or Fact Extraction tabs
4. Check results in the Results Browser

Enjoy! 🎉
