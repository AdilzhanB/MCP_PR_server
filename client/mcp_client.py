"""
MCP Client Implementation
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

class MCPClient:
    """Advanced MCP Client for interacting with MCP servers"""
    
    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.session: Optional[ClientSession] = None
        
    async def connect(self):
        """Connect to the MCP server"""
        server_params = StdioServerParameters(
            command=self.server_command[0],
            args=self.server_command[1:] if len(self.server_command) > 1 else []
        )
        
        self.session = await stdio_client(server_params)
        logger.info("Connected to MCP server")
    
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Disconnected from MCP server")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        result = await self.session.list_tools()
        return [tool.model_dump() for tool in result.tools]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool with arguments"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        result = await self.session.call_tool(name, arguments)
        return {
            "content": [content.model_dump() for content in result.content],
            "isError": result.isError
        }
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        result = await self.session.list_resources()
        return [resource.model_dump() for resource in result.resources]
    
    async def get_resource(self, uri: str) -> Dict[str, Any]:
        """Get resource content"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        result = await self.session.get_resource(uri)
        return {
            "contents": [content.model_dump() for content in result.contents]
        }
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List available prompts"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        result = await self.session.list_prompts()
        return [prompt.model_dump() for prompt in result.prompts]
    
    async def get_prompt(self, name: str, arguments: Dict[str, str]) -> Dict[str, Any]:
        """Get prompt content"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        result = await self.session.get_prompt(name, arguments)
        return {
            "description": result.description,
            "messages": [msg.model_dump() for msg in result.messages]
        }

class WorkflowOrchestrator:
    """Orchestrate complex workflows using MCP tools"""
    
    def __init__(self, client: MCPClient):
        self.client = client
    
    async def run_data_analysis_workflow(self, data: List[float]) -> Dict[str, Any]:
        """Run a complete data analysis workflow"""
        workflow_results = {
            "workflow_id": f"data_analysis_{len(data)}",
            "steps": []
        }
        
        # Step 1: Basic analysis
        basic_result = await self.client.call_tool("analyze_data", {
            "data": data,
            "analysis_type": "basic"
        })
        workflow_results["steps"].append({
            "step": "basic_analysis",
            "result": basic_result
        })
        
        # Step 2: Statistical analysis
        stats_result = await self.client.call_tool("analyze_data", {
            "data": data,
            "analysis_type": "statistical"
        })
        workflow_results["steps"].append({
            "step": "statistical_analysis",
            "result": stats_result
        })
        
        # Step 3: Trend analysis
        trend_result = await self.client.call_tool("analyze_data", {
            "data": data,
            "analysis_type": "trend"
        })
        workflow_results["steps"].append({
            "step": "trend_analysis",
            "result": trend_result
        })
        
        # Step 4: Generate insights prompt
        data_summary = f"Analyzed {len(data)} data points with mean {sum(data)/len(data):.2f}"
        prompt_result = await self.client.get_prompt("data_analysis_prompt", {
            "data_summary": data_summary,
            "analysis_type": "comprehensive"
        })
        workflow_results["steps"].append({
            "step": "insights_generation",
            "result": prompt_result
        })
        
        return workflow_results
    
    async def run_notification_workflow(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a notification workflow for alerts"""
        workflow_results = {
            "workflow_id": f"notification_{alert_data.get('alert_id', 'unknown')}",
            "steps": []
        }
        
        # Determine notification priority and channels
        priority = alert_data.get("severity", "medium")
        message = f"Alert: {alert_data.get('message', 'Unknown alert')}"
        
        # Send Slack notification
        slack_result = await self.client.call_tool("send_notification", {
            "channel": "slack",
            "message": message,
            "recipient": "#alerts",
            "priority": priority
        })
        workflow_results["steps"].append({
            "step": "slack_notification",
            "result": slack_result
        })
        
        # Send email for high priority alerts
        if priority in ["high", "urgent"]:
            email_result = await self.client.call_tool("send_notification", {
                "channel": "email",
                "message": message,
                "recipient": "admin@example.com",
                "priority": priority
            })
            workflow_results["steps"].append({
                "step": "email_notification",
                "result": email_result
            })
        
        return workflow_results

async def main():
    """Example client usage"""
    client = MCPClient(["python", "server/main.py"])
    
    try:
        await client.connect()
        
        # List available tools
        tools = await client.list_tools()
        print("Available tools:")
        for tool in tools:
            print(f"- {tool['name']}: {tool['description']}")
        
        # Example data analysis
        sample_data = [1.2, 2.3, 1.8, 3.1, 2.7, 4.2, 3.8, 2.9, 3.5, 4.1]
        
        # Run workflow
        orchestrator = WorkflowOrchestrator(client)
        workflow_result = await orchestrator.run_data_analysis_workflow(sample_data)
        
        print("\nWorkflow Results:")
        print(json.dumps(workflow_result, indent=2))
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())