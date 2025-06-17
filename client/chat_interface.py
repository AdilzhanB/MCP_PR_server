"""
Interactive Chat Interface for MCP Client
"""

import asyncio
import json
import readline
from typing import List, Dict, Any
from .mcp_client import MCPClient, WorkflowOrchestrator

class MCPChatInterface:
    """Interactive chat interface for MCP operations"""
    
    def __init__(self, server_command: List[str]):
        self.client = MCPClient(server_command)
        self.orchestrator = None
        self.running = False
    
    async def start(self):
        """Start the chat interface"""
        print("🚀 MCP Advanced Chat Interface")
        print("=" * 50)
        
        try:
            await self.client.connect()
            self.orchestrator = WorkflowOrchestrator(self.client)
            
            print("✅ Connected to MCP server")
            await self._show_help()
            
            self.running = True
            while self.running:
                try:
                    command = input("\n🤖 MCP> ").strip()
                    if command:
                        await self._process_command(command)
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except EOFError:
                    break
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await self.client.disconnect()
    
    async def _process_command(self, command: str):
        """Process user commands"""
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        
        try:
            if cmd == "help":
                await self._show_help()
            elif cmd == "tools":
                await self._list_tools()
            elif cmd == "resources":
                await self._list_resources()
            elif cmd == "prompts":
                await self._list_prompts()
            elif cmd == "analyze":
                await self._run_analysis(parts[1:])
            elif cmd == "notify":
                await self._send_notification(parts[1:])
            elif cmd == "workflow":
                await self._run_workflow(parts[1:])
            elif cmd == "resource":
                await self._get_resource(parts[1:])
            elif cmd == "quit" or cmd == "exit":
                self.running = False
            else:
                print(f"❓ Unknown command: {cmd}. Type 'help' for available commands.")
                
        except Exception as e:
            print(f"❌ Command error: {e}")
    
    async def _show_help(self):
        """Show available commands"""
        help_text = """
📋 Available Commands:
  
  🔧 Basic Operations:
    tools                    - List available tools
    resources               - List available resources  
    prompts                 - List available prompts
    resource <uri>          - Get resource content
  
  📊 Data Analysis:
    analyze <type> <data>   - Run data analysis
                             Types: basic, statistical, correlation, trend
                             Data: comma-separated numbers
                             Example: analyze basic 1,2,3,4,5
  
  📢 Notifications:
    notify <channel> <recipient> <message>
                           - Send notification
                           Channels: slack, email, webhook
                           Example: notify slack #alerts "Test message"
  
  🔄 Workflows:
    workflow sample        - Run sample workflow
    workflow analysis      - Run data analysis workflow
  
  ❓ Other:
    help                   - Show this help
    quit/exit             - Exit the interface
"""
        print(help_text)
    
    async def _list_tools(self):
        """List available tools"""
        tools = await self.client.list_tools()
        print("\n🔧 Available Tools:")
        for tool in tools:
            print(f"  • {tool['name']}")
            print(f"    {tool['description']}")
            print()
    
    async def _list_resources(self):
        """List available resources"""
        resources = await self.client.list_resources()
        print("\n📁 Available Resources:")
        for resource in resources:
            print(f"  • {resource['name']} ({resource['uri']})")
            print(f"    {resource['description']}")
            print()
    
    async def _list_prompts(self):
        """List available prompts"""
        prompts = await self.client.list_prompts()
        print("\n💭 Available Prompts:")
        for prompt in prompts:
            print(f"  • {prompt['name']}")
            print(f"    {prompt['description']}")
            print()
    
    async def _run_analysis(self, args: List[str]):
        """Run data analysis"""
        if len(args) < 2:
            print("❌ Usage: analyze <type> <data>")
            print("   Example: analyze basic 1,2,3,4,5")
            return
        
        analysis_type = args[0]
        try:
            data = [float(x.strip()) for x in args[1].split(',')]
        except ValueError:
            print("❌ Invalid data format. Use comma-separated numbers.")
            return
        
        print(f"📊 Running {analysis_type} analysis on {len(data)} data points...")
        
        result = await self.client.call_tool("analyze_data", {
            "data": data,
            "analysis_type": analysis_type
        })
        
        if result.get("isError"):
            print(f"❌ Analysis failed: {result}")
        else:
            content = result["content"][0]["text"]
            analysis_result = json.loads(content)
            self._print_analysis_result(analysis_result)
    
    def _print_analysis_result(self, result: Dict[str, Any]):
        """Pretty print analysis results"""
        print(f"\n📈 Analysis Results ({result.get('analysis_type', 'unknown')}):")
        print("-" * 40)
        
        for key, value in result.items():
            if key == "analysis_type":
                continue
            elif isinstance(value, dict):
                print(f"{key.replace('_', ' ').title()}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            elif isinstance(value, (int, float)):
                print(f"{key.replace('_', ' ').title()}: {value:.3f}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
    
    async def _send_notification(self, args: List[str]):
        """Send notification"""
        if len(args) < 3:
            print("❌ Usage: notify <channel> <recipient> <message>")
            return
        
        channel = args[0]
        recipient = args[1]
        message = " ".join(args[2:])
        
        print(f"📢 Sending {channel} notification to {recipient}...")
        
        result = await self.client.call_tool("send_notification", {
            "channel": channel,
            "message": message,
            "recipient": recipient,
            "priority": "medium"
        })
        
        print(f"✅ Notification result: {result['content'][0]['text']}")
    
    async def _run_workflow(self, args: List[str]):
        """Run workflow"""
        if not args:
            print("❌ Usage: workflow <type>")
            print("   Types: sample, analysis")
            return
        
        workflow_type = args[0]
        
        if workflow_type == "sample":
            await self._run_sample_workflow()
        elif workflow_type == "analysis":
            await self._run_analysis_workflow()
        else:
            print(f"❌ Unknown workflow type: {workflow_type}")
    
    async def _run_sample_workflow(self):
        """Run sample workflow"""
        print("🔄 Running sample workflow...")
        
        workflow_steps = [
            {"step_type": "data_analysis", "parameters": {"data": [1,2,3,4,5], "analysis_type": "basic"}},
            {"step_type": "notification", "parameters": {"channel": "slack", "message": "Analysis complete", "recipient": "#alerts"}}
        ]
        
        result = await self.client.call_tool("process_workflow", {
            "workflow_steps": workflow_steps,
            "trigger_condition": "manual"
        })
        
        workflow_result = json.loads(result["content"][0]["text"])
        print(f"✅ Workflow {workflow_result['workflow_id']} completed:")
        print(f"   Total steps: {workflow_result['total_steps']}")
        print(f"   Completed: {workflow_result['completed_steps']}")
        print(f"   Failed: {workflow_result['failed_steps']}")
    
    async def _run_analysis_workflow(self):
        """Run analysis workflow"""
        data_input = input("📊 Enter data (comma-separated): ").strip()
        try:
            data = [float(x.strip()) for x in data_input.split(',')]
        except ValueError:
            print("❌ Invalid data format")
            return
        
        print("🔄 Running complete analysis workflow...")
        result = await self.orchestrator.run_data_analysis_workflow(data)
        
        print(f"✅ Analysis workflow completed:")
        print(f"   Workflow ID: {result['workflow_id']}")
        print(f"   Steps completed: {len(result['steps'])}")
    
    async def _get_resource(self, args: List[str]):
        """Get resource content"""
        if not args:
            print("❌ Usage: resource <uri>")
            return
        
        uri = args[0]
        print(f"📁 Getting resource: {uri}")
        
        try:
            result = await self.client.get_resource(uri)
            content = result["contents"][0]["text"]
            
            # Try to parse as JSON for pretty printing
            try:
                data = json.loads(content)
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError:
                print(content)
                
        except Exception as e:
            print(f"❌ Error getting resource: {e}")

async def main():
    """Start the chat interface"""
    interface = MCPChatInterface(["python", "server/main.py"])
    await interface.start()

if __name__ == "__main__":
    asyncio.run(main())