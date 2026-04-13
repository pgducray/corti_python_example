#!/bin/bash
# Quick start script for running with Docker Compose

echo "🐳 Starting Corti Application with Docker..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please copy .env-example to .env and configure your credentials:"
    echo "   cp .env-example .env"
    echo ""
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

# Build and start
echo "🔨 Building and starting containers..."
docker-compose up -d

echo ""
echo "✅ Application is starting!"
echo "   Access the app at: http://localhost:8501"
echo ""
echo "💡 Useful commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop:         docker-compose down"
echo "   Restart:      docker-compose restart"
echo ""
