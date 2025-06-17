#!/bin/bash

echo "🖥️ Starting MCP CLI Interface..."
echo "=================================="

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export MCP_DEBUG=true
export MCP_LOG_LEVEL=INFO

# Run CLI interface
python client/chat_interface.py