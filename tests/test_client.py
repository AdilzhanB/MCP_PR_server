"""
Test MCP Client Implementation
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch

# Import client components
from client.mcp_client import MCPClient, WorkflowOrchestrator

class TestMCPClient:
    """Test MCP client functionality"""
    
    @pytest.fixture
    def client(self):
        """Create client instance for testing"""
        return MCPClient(["python", "server/main.py"])
    
    def test_client_initialization(self, client):
        """Test client initializes correctly"""
        assert client.server_command == ["python", "server/main.py"]
        assert client.session is None
    
    @pytest.mark.asyncio
    async def test_connection_management(self, client):
        """Test connection and disconnection"""
        # Mock the stdio_client
        with patch('client.mcp_client.stdio_client') as mock_stdio:
            mock_session = AsyncMock()
            mock_stdio.return_value = mock_session
            
            # Test connection
            await client.connect()
            assert client.session == mock_session
            
            # Test disconnection
            await client.disconnect()
            mock_session.close.assert_called_once()
            assert client.session is None
    
    @pytest.mark.asyncio
    async def test_list_tools(self, client):
        """Test listing tools"""
        # Mock session and tools
        mock_session = AsyncMock()
        mock_tool = Mock()
        mock_tool.model_dump.return_value = {
            "name": "analyze_data",
            "description": "Analyze data using various statistical methods"
        }
        
        mock_result = Mock()
        mock_result.tools = [mock_tool]
        mock_session.list_tools.return_value = mock_result
        
        client.session = mock_session
        
        result = await client.list_tools()
        
        assert len(result) == 1
        assert result[0]["name"] == "analyze_data"
        assert "description" in result[0]
    
    @pytest.mark.asyncio
    async def test_call_tool(self, client):
        """Test calling a tool"""
        # Mock session and tool call
        mock_session = AsyncMock()
        mock_content = Mock()
        mock_content.model_dump.return_value = {
            "type": "text",
            "text": '{"mean": 3.0, "count": 5}'
        }
        
        mock_result = Mock()
        mock_result.content = [mock_content]
        mock_result.isError = False
        mock_session.call_tool.return_value = mock_result
        
        client.session = mock_session
        
        result = await client.call_tool("analyze_data", {
            "data": [1, 2, 3, 4, 5],
            "analysis_type": "basic"
        })
        
        assert "content" in result
        assert "isError" in result
        assert result["isError"] is False
        assert len(result["content"]) == 1
    
    @pytest.mark.asyncio
    async def test_list_resources(self, client):
        """Test listing resources"""
        mock_session = AsyncMock()
        mock_resource = Mock()
        mock_resource.model_dump.return_value = {
            "uri": "data://analytics/dashboard",
            "name": "Analytics Dashboard Data",
            "description": "Real-time analytics dashboard data"
        }
        
        mock_result = Mock()
        mock_result.resources = [mock_resource]
        mock_session.list_resources.return_value = mock_result
        
        client.session = mock_session
        
        result = await client.list_resources()
        
        assert len(result) == 1
        assert result[0]["uri"] == "data://analytics/dashboard"
        assert "name" in result[0]
        assert "description" in result[0]
    
    @pytest.mark.asyncio
    async def test_get_resource(self, client):
        """Test getting resource content"""
        mock_session = AsyncMock()
        mock_content = Mock()
        mock_content.model_dump.return_value = {
            "type": "text",
            "text": '{"dashboard_id": "main_analytics"}'
        }
        
        mock_result = Mock()
        mock_result.contents = [mock_content]
        mock_session.get_resource.return_value = mock_result
        
        client.session = mock_session
        
        result = await client.get_resource("data://analytics/dashboard")
        
        assert "contents" in result
        assert len(result["contents"]) == 1
    
    @pytest.mark.asyncio
    async def test_not_connected_error(self, client):
        """Test error when not connected"""
        with pytest.raises(RuntimeError) as excinfo:
            await client.list_tools()
        
        assert "Not connected to server" in str(excinfo.value)

class TestWorkflowOrchestrator:
    """Test workflow orchestration functionality"""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock client for testing"""
        client = AsyncMock(spec=MCPClient)
        return client
    
    @pytest.fixture
    def orchestrator(self, mock_client):
        """Create orchestrator instance with mock client"""
        return WorkflowOrchestrator(mock_client)
    
    @pytest.mark.asyncio
    async def test_data_analysis_workflow(self, orchestrator, mock_client):
        """Test data analysis workflow"""
        # Mock tool call responses
        mock_responses = [
            {
                "content": [{"text": '{"mean": 3.0, "analysis_type": "basic"}'}],
                "isError": False
            },
            {
                "content": [{"text": '{"mean": 3.0, "std": 1.41, "analysis_type": "statistical"}'}],
                "isError": False
            },
            {
                "content": [{"text": '{"slope": 0.5, "analysis_type": "trend"}'}],
                "isError": False
            }
        ]
        
        mock_prompt_response = {
            "description": "Generated insights",
            "messages": [{"role": "user", "content": {"type": "text", "text": "Analysis prompt"}}]
        }
        
        mock_client.call_tool.side_effect = mock_responses
        mock_client.get_prompt.return_value = mock_prompt_response
        
        result = await orchestrator.run_data_analysis_workflow([1, 2, 3, 4, 5])
        
        assert "workflow_id" in result
        assert "steps" in result
        assert len(result["steps"]) == 4  # 3 analysis + 1 prompt
        
        # Verify correct tools were called
        expected_calls = [
            ("analyze_data", {"data": [1, 2, 3, 4, 5], "analysis_type": "basic"}),
            ("analyze_data", {"data": [1, 2, 3, 4, 5], "analysis_type": "statistical"}),
            ("analyze_data", {"data": [1, 2, 3, 4, 5], "analysis_type": "trend"})
        ]
        
        actual_calls = [call.args for call in mock_client.call_tool.call_args_list]
        assert actual_calls == expected_calls
    
    @pytest.mark.asyncio
    async def test_notification_workflow(self, orchestrator, mock_client):
        """Test notification workflow"""
        # Mock notification responses
        mock_slack_response = {
            "content": [{"text": '{"status": "sent", "channel": "slack"}'}],
            "isError": False
        }
        
        mock_email_response = {
            "content": [{"text": '{"status": "sent", "channel": "email"}'}],
            "isError": False
        }
        
        mock_client.call_tool.side_effect = [mock_slack_response, mock_email_response]
        
        alert_data = {
            "alert_id": "test_alert_123",
            "severity": "high",
            "message": "Critical system alert detected by AdilzhanB",
            "timestamp": "2025-06-17T04:34:37Z"
        }
        
        result = await orchestrator.run_notification_workflow(alert_data)
        
        assert "workflow_id" in result
        assert "steps" in result
        assert len(result["steps"]) == 2  # Slack + Email for high priority
        
        # Verify Slack notification was called
        slack_call = mock_client.call_tool.call_args_list[0]
        assert slack_call.args[0] == "send_notification"
        assert slack_call.args[1]["channel"] == "slack"
        assert slack_call.args[1]["priority"] == "high"
    
    @pytest.mark.asyncio
    async def test_notification_workflow_medium_priority(self, orchestrator, mock_client):
        """Test notification workflow with medium priority (Slack only)"""
        mock_slack_response = {
            "content": [{"text": '{"status": "sent", "channel": "slack"}'}],
            "isError": False
        }
        
        mock_client.call_tool.return_value = mock_slack_response
        
        alert_data = {
            "alert_id": "test_alert_456",
            "severity": "medium",
            "message": "System notification from AdilzhanB"
        }
        
        result = await orchestrator.run_notification_workflow(alert_data)
        
        assert len(result["steps"]) == 1  # Only Slack for medium priority
        
        # Verify only Slack was called
        assert mock_client.call_tool.call_count == 1
        slack_call = mock_client.call_tool.call_args_list[0]
        assert slack_call.args[1]["priority"] == "medium"

class TestClientIntegration:
    """Integration tests for client functionality"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test end-to-end workflow simulation"""
        # This would be an integration test that actually connects to a running server
        # For now, we'll simulate it with mocks
        
        with patch('client.mcp_client.stdio_client') as mock_stdio:
            # Setup mock session
            mock_session = AsyncMock()
            mock_stdio.return_value = mock_session
            
            # Mock tool listing
            mock_tool = Mock()
            mock_tool.model_dump.return_value = {
                "name": "analyze_data",
                "description": "Analyze data"
            }
            mock_list_result = Mock()
            mock_list_result.tools = [mock_tool]
            mock_session.list_tools.return_value = mock_list_result
            
            # Mock tool call
            mock_call_content = Mock()
            mock_call_content.model_dump.return_value = {
                "type": "text",
                "text": '{"mean": 3.0, "count": 5, "analysis_type": "basic"}'
            }
            mock_call_result = Mock()
            mock_call_result.content = [mock_call_content]
            mock_call_result.isError = False
            mock_session.call_tool.return_value = mock_call_result
            
            # Test the workflow
            client = MCPClient(["python", "server/main.py"])
            
            await client.connect()
            
            # List tools
            tools = await client.list_tools()
            assert len(tools) == 1
            assert tools[0]["name"] == "analyze_data"
            
            # Call tool
            result = await client.call_tool("analyze_data", {
                "data": [1, 2, 3, 4, 5],
                "analysis_type": "basic"
            })
            
            assert not result["isError"]
            content = result["content"][0]["text"]
            analysis_result = json.loads(content)
            assert analysis_result["mean"] == 3.0
            assert analysis_result["count"] == 5
            
            await client.disconnect()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])