#!/bin/bash

echo "🌐 Starting MCP Web Interface..."
echo "=================================="

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export WEB_HOST=0.0.0.0
export WEB_PORT=8000
export WEB_RELOAD=true
export MCP_DEBUG=false

# Run web service
python web_service/app.py