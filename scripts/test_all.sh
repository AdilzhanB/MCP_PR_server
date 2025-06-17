#!/bin/bash

echo "🧪 Running All Tests..."
echo "======================="

# Activate virtual environment
source venv/bin/activate

# Run server tests
echo "📡 Testing MCP Server..."
python -m pytest tests/test_server.py -v

# Run client tests
echo "💻 Testing MCP Client..."
python -m pytest tests/test_client.py -v

# Run web service tests
echo "🌐 Testing Web Service..."
python -m pytest tests/test_web_service.py -v

# Run integration tests
echo "🔗 Running Integration Tests..."
python -m pytest tests/ -v --cov=server --cov=client --cov=web_service

echo "✅ All tests completed!"