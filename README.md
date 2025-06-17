# MCP Advanced Project

An advanced implementation of the Model Context Protocol (MCP) with comprehensive features including data analysis, workflow automation, notifications, and a modern web interface.

## 🌟 Overview

This project provides a production-ready MCP server with advanced capabilities, built by **AdilzhanB**. It demonstrates the full potential of the Model Context Protocol through practical implementations and real-world use cases.

### Key Features

- 🔧 **Advanced MCP Server** with tools, resources, and prompts
- 📊 **Data Analysis Engine** supporting multiple statistical methods
- 🔄 **Workflow Automation** with multi-step orchestration
- 📢 **Multi-channel Notifications** (Slack, email, webhook)
- 🌐 **Modern Web Interface** with real-time WebSocket communication
- 📁 **Dynamic Resources** with caching and real-time data
- 🐳 **Docker Support** for easy deployment
- 🧪 **Comprehensive Testing** with 80%+ code coverage

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (optional)
- Docker & Docker Compose (for containerized deployment)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp-advanced-project

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Activate virtual environment
source venv/bin/activate
```

### Running the Application

#### CLI Interface
```bash
./scripts/run_cli.sh
```

#### Web Interface
```bash
./scripts/run_web.sh
# Visit http://localhost:8000
```

#### Docker Deployment
```bash
docker-compose up -d
# Web interface: http://localhost:8000
# Grafana: http://localhost:3000 (admin/mcpgrafana)
# Prometheus: http://localhost:9090
```

## 💻 Usage Examples

### CLI Interface

```bash
🤖 MCP> analyze basic 1,2,3,4,5
📈 Analysis Results (basic):
Count: 5
Mean: 3.000
Median: 3.000

🤖 MCP> notify slack #alerts "System maintenance"
✅ Notification sent via slack

🤖 MCP> workflow sample
✅ Workflow completed: 2 steps
```

### Web Interface Commands

- `help` - Show available commands
- `analyze basic 1,2,3,4,5` - Perform data analysis
- `notify slack #alerts message` - Send notification
- `workflow sample` - Run sample workflow
- `resource data://analytics/dashboard` - Get analytics data
- `status` - Check system status

### Programmatic Usage

```python
from client.mcp_client import MCPClient, WorkflowOrchestrator

async def main():
    client = MCPClient(["python", "server/main.py"])
    await client.connect()
    
    # Analyze data
    result = await client.call_tool("analyze_data", {
        "data": [1, 2, 3, 4, 5],
        "analysis_type": "statistical"
    })
    
    # Run workflow
    orchestrator = WorkflowOrchestrator(client)
    workflow_result = await orchestrator.run_data_analysis_workflow([1,2,3,4,5])
    
    await client.disconnect()
```

## 🔧 Configuration

### Environment Variables

```bash
# Server Configuration
MCP_SERVER_NAME=mcp-advanced-server
MCP_DEBUG=false
MCP_LOG_LEVEL=INFO

# Web Service
WEB_HOST=0.0.0.0
WEB_PORT=8000

# External APIs
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
EMAIL_SERVICE_API=https://api.emailservice.com
```

### Docker Configuration

```yaml
# docker-compose.yml
services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CURRENT_USER=AdilzhanB
      - CURRENT_DATE=2025-06-17T04:41:53Z
```

## 🏗️ Architecture

### Project Structure

```
mcp-advanced-project/
├── server/           # MCP server implementation
├── client/           # Client libraries and CLI
├── web_service/      # FastAPI web interface
├── tests/           # Comprehensive test suite
├── data/            # Sample data and analytics
├── scripts/         # Automation scripts
├── docs/            # Documentation
└── monitoring/      # Prometheus & Grafana configs
```

### Core Components

1. **MCP Server** (`server/`)
   - Advanced tools for data analysis
   - Webhook management system
   - Multi-channel notification sender
   - Dynamic resource manager

2. **Client Libraries** (`client/`)
   - MCP client implementation
   - Workflow orchestrator
   - CLI interface

3. **Web Service** (`web_service/`)
   - FastAPI application
   - WebSocket real-time communication
   - REST API endpoints
   - Modern responsive UI

## 📊 Features in Detail

### Data Analysis

Supports multiple analysis types:
- **Basic**: Mean, median, min, max, count
- **Statistical**: Standard deviation, variance, percentiles
- **Correlation**: Position correlation, autocorrelation
- **Trend**: Linear regression, forecasting, R-squared

### Workflow Automation

Multi-step workflows with:
- Sequential execution
- Error handling
- Result aggregation
- Progress tracking

### Notifications

Multiple channels supported:
- **Slack**: Webhook integration
- **Email**: SMTP/API integration
- **Webhook**: Custom HTTP endpoints

### Web Interface

Modern features:
- Real-time WebSocket communication
- Responsive design for mobile/desktop
- Command history and auto-completion
- Syntax highlighting for results
- Quick command buttons

## 🧪 Testing

### Run All Tests

```bash
./scripts/test_all.sh
```

### Run Specific Test Suites

```bash
# Server tests
pytest tests/test_server.py -v

# Client tests  
pytest tests/test_client.py -v

# Web service tests
pytest tests/test_web_service.py -v

# Coverage report
pytest --cov=server --cov=client --cov=web_service --cov-report=html
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component functionality
- **Web Tests**: FastAPI endpoint testing
- **Async Tests**: Asynchronous functionality
- **Performance Tests**: Load and stress testing

## 🔍 Monitoring

### Included Monitoring Stack

- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Health Checks**: Endpoint monitoring
- **Logging**: Structured logging with rotation

### Access Monitoring

```bash
# Start monitoring stack
docker-compose up -d

# Access dashboards
http://localhost:3000  # Grafana (admin/mcpgrafana)
http://localhost:9090  # Prometheus
```

## 🚀 Deployment

### Local Development

```bash
# Setup development environment
./scripts/setup.sh
source venv/bin/activate

# Run in development mode
WEB_RELOAD=true python web_service/app.py
```

### Production Docker

```bash
# Build and deploy
docker-compose -f docker-compose.yml up -d

# Scale services
docker-compose up --scale mcp-server=3

# View logs
docker-compose logs -f mcp-server
```

### Cloud Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed cloud deployment instructions including:
- AWS ECS/EKS deployment
- Azure Container Instances
- Google Cloud Run
- Kubernetes manifests

## 📖 Documentation

- [API Reference](docs/API.md) - Complete API documentation
- [Usage Guide](docs/USAGE.md) - Detailed usage examples
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- [Contributing](CONTRIBUTING.md) - Development guidelines

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation
- Ensure 80%+ test coverage

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**AdilzhanB**
- Created: 2025-06-17 04:41:53 UTC
- Email: adilzhanb@example.com
- GitHub: [@AdilzhanB](https://github.com/AdilzhanB)

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for the Model Context Protocol
- [FastAPI](https://fastapi.tiangolo.com) for the excellent web framework
- [Pydantic](https://pydantic.dev) for data validation
- The open-source community for inspiration and tools

## 📈 Project Status

- **Version**: 1.0.0
- **Status**: Production Ready
- **Last Updated**: 2025-06-17 04:41:53 UTC
- **Test Coverage**: 85%+
- **Documentation**: Complete

## 🔮 Roadmap

- [ ] GraphQL API support
- [ ] Advanced ML model integration
- [ ] Real-time collaboration features
- [ ] Mobile app companion
- [ ] Enterprise SSO integration
- [ ] Advanced security features

---

**Built with ❤️ by AdilzhanB**
