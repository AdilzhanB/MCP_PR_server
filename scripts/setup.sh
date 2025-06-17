#!/bin/bash

echo "🚀 Setting up MCP Advanced Project..."
echo "======================================"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "📍 Python version: $python_version"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data logs

# Copy environment file
echo "⚙️ Setting up environment..."
cp .env.example .env

# Create sample data
echo "💾 Creating sample data..."
cat > data/sample_data.json << 'EOF'
{
  "datasets": {
    "sales": [1200, 1350, 1100, 980, 1450, 1600, 1200, 1800, 1900, 2100],
    "users": [45, 52, 38, 41, 67, 72, 55, 89, 95, 102],
    "performance": [85.2, 87.1, 84.3, 86.7, 88.9, 91.2, 89.5, 92.1, 90.8, 93.4]
  },
  "metadata": {
    "created": "2025-06-16T13:46:16Z",
    "version": "1.0.0",
    "description": "Sample datasets for MCP analysis"
  }
}
EOF

cat > data/analytics.json << 'EOF'
{
  "dashboard": {
    "total_requests": 15847,
    "active_users": 342,
    "response_time_avg": 145.7,
    "error_rate": 0.8,
    "uptime_percentage": 99.97
  },
  "trends": {
    "requests_24h": [1200, 1350, 1100, 980, 1450, 1600, 1200],
    "users_24h": [45, 52, 38, 41, 67, 72, 55],
    "errors_24h": [2, 1, 0, 3, 1, 2, 1]
  },
  "last_updated": "2025-06-16T13:46:16Z"
}
EOF

# Make scripts executable
echo "🔐 Making scripts executable..."
chmod +x scripts/*.sh

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Run CLI interface: ./scripts/run_cli.sh"
echo "   3. Run web interface: ./scripts/run_web.sh"
echo "   4. Run tests: ./scripts/test_all.sh"
echo ""
echo "🌐 Web interface will be available at: http://localhost:8000"
echo "👤 Current user: AdilzhanB"
echo "📅 Setup date: 2025-06-16 13:46:16 UTC"