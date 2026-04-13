#!/bin/bash
# Quick start script for running Streamlit locally

echo "🚀 Starting Corti Streamlit Application..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please copy .env-example to .env and configure your credentials:"
    echo "   cp .env-example .env"
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run Streamlit
echo ""
echo "✅ Starting Streamlit on http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""
streamlit run app/streamlit_app.py
