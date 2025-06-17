"""
Test MCP Server Implementation
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

# Import server components
from server.main import AdvancedMCPServer
from server.tools import DataAnalyzer, WebhookManager, NotificationSender
from server.resources import DataResourceManager
from server.config import MCPConfig

class TestAdvancedMCPServer:
    """Test the main MCP server functionality"""
    
    @pytest.fixture
    def server(self):
        """Create server instance for testing"""
        return AdvancedMCPServer()
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing"""
        return [1.2, 2.3, 1.8, 3.1, 2.7, 4.2, 3.8, 2.9, 3.5, 4.1]
    
    def test_server_initialization(self, server):
        """Test server initializes correctly"""
        assert server.server is not None
        assert server.config is not None
        assert server.data_analyzer is not None
        assert server.webhook_manager is not None
        assert server.notification_sender is not None
        assert server.resource_manager is not None
    
    def test_config_loading(self):
        """Test configuration loading"""
        config = MCPConfig()
        
        assert config.get("server.name") == "advanced-mcp-server"
        assert config.get("server.version") == "1.0.0"
        assert config.get("features.data_analysis") is True
        assert config.get("features.webhooks") is True
        assert config.get("features.notifications") is True
        assert config.get("features.workflows") is True

class TestDataAnalyzer:
    """Test data analysis functionality"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return DataAnalyzer()
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for analysis"""
        return [1.0, 2.0, 3.0, 4.0, 5.0]
    
    @pytest.mark.asyncio
    async def test_basic_analysis(self, analyzer, sample_data):
        """Test basic statistical analysis"""
        result = await analyzer.analyze(sample_data, "basic")
        
        assert "count" in result
        assert "mean" in result
        assert "median" in result
        assert "min" in result
        assert "max" in result
        
        assert result["count"] == 5
        assert result["mean"] == 3.0
        assert result["median"] == 3.0
        assert result["min"] == 1.0
        assert result["max"] == 5.0
        assert result["analysis_type"] == "basic"
    
    @pytest.mark.asyncio
    async def test_statistical_analysis(self, analyzer, sample_data):
        """Test advanced statistical analysis"""
        result = await analyzer.analyze(sample_data, "statistical")
        
        assert "standard_deviation" in result
        assert "variance" in result
        assert "percentiles" in result
        assert "coefficient_of_variation" in result
        
        # Check basic stats are included
        assert result["mean"] == 3.0
        assert result["analysis_type"] == "statistical"
    
    @pytest.mark.asyncio
    async def test_trend_analysis(self, analyzer, sample_data):
        """Test trend analysis"""
        result = await analyzer.analyze(sample_data, "trend")
        
        assert "trend_slope" in result
        assert "trend_intercept" in result
        assert "r_squared" in result
        assert "forecast_next_3" in result
        
        assert result["analysis_type"] == "trend"
        assert isinstance(result["forecast_next_3"], list)
        assert len(result["forecast_next_3"]) == 3
    
    @pytest.mark.asyncio
    async def test_correlation_analysis(self, analyzer, sample_data):
        """Test correlation analysis"""
        result = await analyzer.analyze(sample_data, "correlation")
        
        assert "position_correlation" in result
        assert "autocorrelation_lag1" in result
        assert "trend_direction" in result
        
        assert result["analysis_type"] == "correlation"
    
    @pytest.mark.asyncio
    async def test_empty_data_handling(self, analyzer):
        """Test handling of empty data"""
        result = await analyzer.analyze([], "basic")
        
        assert "error" in result
        assert result["error"] == "No data provided"
    
    @pytest.mark.asyncio
    async def test_invalid_analysis_type(self, analyzer, sample_data):
        """Test handling of invalid analysis type"""
        result = await analyzer.analyze(sample_data, "invalid_type")
        
        assert "error" in result
        assert "Unknown analysis type" in result["error"]

class TestWebhookManager:
    """Test webhook management functionality"""
    
    @pytest.fixture
    def webhook_manager(self):
        """Create webhook manager instance"""
        return WebhookManager()
    
    @pytest.mark.asyncio
    async def test_webhook_setup(self, webhook_manager):
        """Test webhook setup"""
        endpoint = "https://example.com/webhook"
        events = ["data_analysis", "notification"]
        secret = "test_secret"
        
        result = await webhook_manager.setup_webhook(endpoint, events, secret)
        
        assert "webhook_id" in result
        assert "status" in result
        assert result["status"] == "created"
        assert result["endpoint"] == endpoint
        assert result["events"] == events
    
    @pytest.mark.asyncio
    async def test_webhook_trigger(self, webhook_manager):
        """Test webhook triggering"""
        endpoint = "https://httpbin.org/post"  # Test endpoint
        payload = {"test": "data", "timestamp": "2025-06-17T04:34:37Z"}
        
        # Mock aiohttp to avoid actual HTTP calls in tests
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text.return_value = '{"success": true}'
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await webhook_manager.trigger_webhook(endpoint, payload)
            
            assert result["status"] == "success"
            assert result["response_code"] == 200

class TestNotificationSender:
    """Test notification sending functionality"""
    
    @pytest.fixture
    def notification_sender(self):
        """Create notification sender instance"""
        return NotificationSender()
    
    @pytest.mark.asyncio
    async def test_slack_notification(self, notification_sender):
        """Test Slack notification sending"""
        result = await notification_sender.send(
            channel="slack",
            message="Test message from AdilzhanB",
            recipient="#test-channel",
            priority="medium"
        )
        
        assert "notification_id" in result
        assert result["channel"] == "slack"
        assert result["status"] == "sent"
        assert result["recipient"] == "#test-channel"
        assert result["priority"] == "medium"
    
    @pytest.mark.asyncio
    async def test_email_notification(self, notification_sender):
        """Test email notification sending"""
        result = await notification_sender.send(
            channel="email",
            message="Test email from AdilzhanB",
            recipient="test@example.com",
            priority="high"
        )
        
        assert "notification_id" in result
        assert result["channel"] == "email"
        assert result["status"] == "sent"
        assert result["recipient"] == "test@example.com"
        assert result["priority"] == "high"
    
    @pytest.mark.asyncio
    async def test_webhook_notification(self, notification_sender):
        """Test webhook notification sending"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await notification_sender.send(
                channel="webhook",
                message="Test webhook notification",
                recipient="https://example.com/webhook",
                priority="urgent"
            )
            
            assert result["channel"] == "webhook"
            assert result["status"] == "sent"
    
    @pytest.mark.asyncio
    async def test_unknown_channel(self, notification_sender):
        """Test handling of unknown notification channel"""
        result = await notification_sender.send(
            channel="unknown_channel",
            message="Test message",
            recipient="test",
            priority="medium"
        )
        
        assert result["status"] == "error"
        assert "Unknown channel" in result["error"]

class TestDataResourceManager:
    """Test data resource management functionality"""
    
    @pytest.fixture
    def resource_manager(self):
        """Create resource manager instance"""
        return DataResourceManager()
    
    @pytest.mark.asyncio
    async def test_analytics_resource(self, resource_manager):
        """Test analytics resource retrieval"""
        result = await resource_manager.get_resource("data://analytics/dashboard")
        
        assert "dashboard_id" in result
        assert "generated_at" in result
        assert "metrics" in result
        assert "trends" in result
        
        # Check specific metrics
        metrics = result["metrics"]
        assert "total_requests" in metrics
        assert "active_users" in metrics
        assert "response_time_avg" in metrics
        assert "error_rate" in metrics
        assert "uptime_percentage" in metrics
    
    @pytest.mark.asyncio
    async def test_server_config_resource(self, resource_manager):
        """Test server configuration resource"""
        result = await resource_manager.get_resource("config://server/settings")
        
        assert "server_name" in result
        assert "version" in result
        assert "features" in result
        assert "security" in result
        assert "logging" in result
        
        assert result["server_name"] == "advanced-mcp-server"
        assert result["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_logs_resource(self, resource_manager):
        """Test system logs resource"""
        result = await resource_manager.get_resource("logs://system/recent")
        
        assert isinstance(result, str)
        assert "INFO:" in result or "DEBUG:" in result or "WARNING:" in result
        assert "Server started successfully" in result
    
    @pytest.mark.asyncio
    async def test_unknown_resource(self, resource_manager):
        """Test handling of unknown resource URI"""
        with pytest.raises(ValueError) as excinfo:
            await resource_manager.get_resource("unknown://resource/uri")
        
        assert "Unknown resource URI" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_resource_caching(self, resource_manager):
        """Test resource caching functionality"""
        # First call
        result1 = await resource_manager.get_resource("data://analytics/dashboard")
        
        # Second call (should use cache)
        result2 = await resource_manager.get_resource("data://analytics/dashboard")
        
        # Results should be identical (from cache)
        assert result1["dashboard_id"] == result2["dashboard_id"]

class TestWorkflowProcessing:
    """Test workflow processing functionality"""
    
    @pytest.fixture
    def server(self):
        """Create server instance for testing"""
        return AdvancedMCPServer()
    
    @pytest.mark.asyncio
    async def test_simple_workflow(self, server):
        """Test simple workflow processing"""
        workflow_steps = [
            {
                "step_type": "data_analysis",
                "parameters": {
                    "data": [1, 2, 3, 4, 5],
                    "analysis_type": "basic"
                }
            }
        ]
        
        result = await server._process_workflow(
            workflow_steps=workflow_steps,
            trigger_condition="test_trigger"
        )
        
        assert "workflow_id" in result
        assert "total_steps" in result
        assert "completed_steps" in result
        assert "failed_steps" in result
        assert "steps" in result
        
        assert result["total_steps"] == 1
        assert result["completed_steps"] == 1
        assert result["failed_steps"] == 0
        assert result["trigger_condition"] == "test_trigger"
    
    @pytest.mark.asyncio
    async def test_multi_step_workflow(self, server):
        """Test multi-step workflow processing"""
        workflow_steps = [
            {
                "step_type": "data_analysis",
                "parameters": {
                    "data": [1.0, 2.0, 3.0],
                    "analysis_type": "basic"
                }
            },
            {
                "step_type": "notification",
                "parameters": {
                    "channel": "slack",
                    "message": "Analysis complete by AdilzhanB",
                    "recipient": "#alerts"
                }
            }
        ]
        
        result = await server._process_workflow(
            workflow_steps=workflow_steps,
            trigger_condition="multi_step_test"
        )
        
        assert result["total_steps"] == 2
        assert result["completed_steps"] == 2
        assert result["failed_steps"] == 0
    
    @pytest.mark.asyncio
    async def test_workflow_with_error(self, server):
        """Test workflow handling with error step"""
        workflow_steps = [
            {
                "step_type": "unknown_step_type",
                "parameters": {}
            }
        ]
        
        result = await server._process_workflow(
            workflow_steps=workflow_steps
        )
        
        assert result["total_steps"] == 1
        assert result["completed_steps"] == 0
        assert result["failed_steps"] == 0  # Unknown steps are skipped, not failed
        
        step_result = result["steps"][0]
        assert step_result["status"] == "skipped"
        assert "Unknown step type" in step_result["reason"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])