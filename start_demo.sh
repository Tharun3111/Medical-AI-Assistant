#!/bin/bash

# Doctor Bot LLM-as-Judge Demo Startup Script

echo "🏥 Starting Doctor Bot LLM-as-Judge Demo"
echo "========================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file and set your GEMINI_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Check if GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env; then
    echo "✅ GEMINI_API_KEY appears to be configured"
else
    echo "❌ Please set your GEMINI_API_KEY in the .env file"
    exit 1
fi

# Check if data is processed
if [ ! -f "data/processed/faiss.index" ]; then
    echo "📚 Building vector index..."
    echo "   This may take a few minutes on first run..."
    bash scripts/01_ingest.sh
    bash scripts/02_build_index.sh
    echo "✅ Index built successfully"
else
    echo "✅ Vector index found"
fi

# Install Streamlit dependencies if needed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing Streamlit dependencies..."
    pip install -r requirements_streamlit.txt
fi

echo ""
echo "🚀 Starting services..."
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $API_PID $STREAMLIT_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start API in background
echo "🔧 Starting API server on http://127.0.0.1:8000"
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000 &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Check if API is running
if ! curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "❌ API failed to start. Check the logs above."
    exit 1
fi

echo "✅ API is running"

# Start Streamlit
echo "🌐 Starting Streamlit UI on http://localhost:8501"
streamlit run streamlit_app.py --server.port 8501 --server.address localhost &
STREAMLIT_PID=$!

echo ""
echo "🎉 Demo is ready!"
echo ""
echo "📱 Streamlit UI: http://localhost:8501"
echo "🔧 API Docs: http://127.0.0.1:8000/docs"
echo "❤️  Health Check: http://127.0.0.1:8000/health"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait
