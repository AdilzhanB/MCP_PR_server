"""
Enhanced MCP Web Service with Full Features
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uvicorn
from pathlib import Path

from client.mcp_client import MCPClient, WorkflowOrchestrator
from server.config import MCPConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MCP Advanced Web Interface",
    description="Web interface for Model Context Protocol server",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files and templates
web_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=web_dir / "static"), name="static")
templates = Jinja2Templates(directory=web_dir / "templates")

# Configuration
config = MCPConfig()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.mcp_client: Optional[MCPClient] = None
        self.orchestrator: Optional[WorkflowOrchestrator] = None
        self.connection_count = 0

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_count += 1
        
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
        
        # Initialize MCP client if not already done
        if not self.mcp_client:
            try:
                self.mcp_client = MCPClient(["python", "server/main.py"])
                await self.mcp_client.connect()
                self.orchestrator = WorkflowOrchestrator(self.mcp_client)
                logger.info("MCP client connected successfully")
            except Exception as e:
                logger.error(f"Failed to connect MCP client: {e}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def broadcast(self, message: str):
        for connection in self.active_connections[:]:  # Copy to avoid modification during iteration
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                self.active_connections.remove(connection)

manager = ConnectionManager()

# API Routes
@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    """Serve the main chat page"""
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "user_login": "AdilzhanB",
        "current_time": current_time,
        "server_name": config.get("server.name", "MCP Advanced Server"),
        "version": config.get("server.version", "1.0.0")
    })

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mcp_connected": manager.mcp_client is not None,
        "active_connections": len(manager.active_connections),
        "server_info": {
            "name": config.get("server.name"),
            "version": config.get("server.version"),
            "debug": config.get("server.debug")
        }
    }

@app.get("/api/tools")
async def get_tools():
    """Get available MCP tools"""
    if not manager.mcp_client:
        raise HTTPException(status_code=503, detail="MCP client not connected")
    
    try:
        tools = await manager.mcp_client.list_tools()
        return {"tools": tools}
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resources")
async def get_resources():
    """Get available MCP resources"""
    if not manager.mcp_client:
        raise HTTPException(status_code=503, detail="MCP client not connected")
    
    try:
        resources = await manager.mcp_client.list_resources()
        return {"resources": resources}
    except Exception as e:
        logger.error(f"Error getting resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_data(data: Dict[str, Any]):
    """Analyze data via REST API"""
    if not manager.mcp_client:
        raise HTTPException(status_code=503, detail="MCP client not connected")
    
    try:
        result = await manager.mcp_client.call_tool("analyze_data", data)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error analyzing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        welcome_msg = {
            "type": "system",
            "message": f"🚀 Welcome to MCP Advanced Interface, AdilzhanB!",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": "System",
            "metadata": {
                "connection_id": manager.connection_count,
                "server_time": "2025-06-16 13:46:16",
                "features_enabled": ["data_analysis", "workflows", "notifications"]
            }
        }
        await manager.send_personal_message(json.dumps(welcome_msg), websocket)
        
        # Send available commands
        help_msg = {
            "type": "help",
            "message": await get_help_text(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": "System"
        }
        await manager.send_personal_message(json.dumps(help_msg), websocket)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Log user command
            logger.info(f"User command: {message_data['message']}")
            
            # Process the command
            response = await process_chat_command(
                message_data["message"], 
                message_data["user"]
            )
            
            # Send response back
            await manager.send_personal_message(json.dumps(response), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        error_msg = {
            "type": "error",
            "message": f"❌ Connection error: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": "System"
        }
        try:
            await manager.send_personal_message(json.dumps(error_msg), websocket)
        except:
            pass
        manager.disconnect(websocket)

async def process_chat_command(command: str, user: str) -> Dict[str, Any]:
    """Process chat commands and return response"""
    timestamp = datetime.now(timezone.utc).isoformat()
    
    try:
        parts = command.strip().split()
        if not parts:
            return {
                "type": "error",
                "message": "❓ Please enter a command. Type 'help' for available commands.",
                "timestamp": timestamp,
                "user": "System"
            }
        
        cmd = parts[0].lower()
        
        if cmd == "help":
            return {
                "type": "help",
                "message": await get_help_text(),
                "timestamp": timestamp,
                "user": "System"
            }
        
        elif cmd == "status":
            status_info = {
                "server": "MCP Advanced Server v1.0.0",
                "user": "AdilzhanB",
                "time": "2025-06-16 13:46:16 UTC",
                "connections": len(manager.active_connections),
                "mcp_connected": manager.mcp_client is not None
            }
            
            status_text = "📊 **System Status**\n\n"
            for key, value in status_info.items():
                status_text += f"• **{key.replace('_', ' ').title()}**: {value}\n"
            
            return {
                "type": "status",
                "message": status_text,
                "timestamp": timestamp,
                "user": "System",
                "data": status_info
            }
        
        elif cmd == "tools":
            if not manager.mcp_client:
                return {
                    "type": "error",
                    "message": "❌ MCP client not connected",
                    "timestamp": timestamp,
                    "user": "System"
                }
            
            tools = await manager.mcp_client.list_tools()
            tools_text = "🔧 **Available Tools:**\n\n"
            for tool in tools:
                tools_text += f"• **{tool['name']}**: {tool['description']}\n"
            
            return {
                "type": "tools",
                "message": tools_text,
                "timestamp": timestamp,
                "user": "System",
                "data": tools
            }
        
        elif cmd == "analyze":
            return await handle_analyze_command(parts, timestamp)
        
        elif cmd == "notify":
            return await handle_notify_command(parts, timestamp)
        
        elif cmd == "workflow":
            return await handle_workflow_command(parts, timestamp)
        
        elif cmd == "resource":
            return await handle_resource_command(parts, timestamp)
        
        elif cmd == "sample":
            return await handle_sample_command(parts, timestamp)
        
        else:
            return {
                "type": "error",
                "message": f"❓ Unknown command: **{cmd}**. Type 'help' for available commands.",
                "timestamp": timestamp,
                "user": "System"
            }
    
    except Exception as e:
        logger.error(f"Command processing error: {e}")
        return {
            "type": "error",
            "message": f"❌ Error processing command: {str(e)}",
            "timestamp": timestamp,
            "user": "System"
        }

async def handle_analyze_command(parts: List[str], timestamp: str) -> Dict[str, Any]:
    """Handle analyze command"""
    if len(parts) < 3:
        return {
            "type": "error",
            "message": "❌ **Usage**: `analyze <type> <data>`\n\n**Examples**:\n• `analyze basic 1,2,3,4,5`\n• `analyze statistical 10,20,15,25,30`\n• `analyze trend 1,3,2,4,5,7,6,8`\n\n**Types**: basic, statistical, correlation, trend",
            "timestamp": timestamp,
            "user": "System"
        }
    
    analysis_type = parts[1]
    try:
        if parts[2] == "sample":
            # Use sample data
            sample_datasets = {
                "sales": [1200, 1350, 1100, 980, 1450, 1600, 1200, 1800, 1900, 2100],
                "performance": [85.2, 87.1, 84.3, 86.7, 88.9, 91.2, 89.5, 92.1, 90.8, 93.4]
            }
            data = sample_datasets.get("sales", [1,2,3,4,5])
        else:
            data = [float(x.strip()) for x in parts[2].split(',')]
    except ValueError:
        return {
            "type": "error",
            "message": "❌ Invalid data format. Use comma-separated numbers or 'sample'.",
            "timestamp": timestamp,
            "user": "System"
        }
    
    if not manager.mcp_client:
        return {
            "type": "error",
            "message": "❌ MCP client not connected",
            "timestamp": timestamp,
            "user": "System"
        }
    
    try:
        result = await manager.mcp_client.call_tool("analyze_data", {
            "data": data,
            "analysis_type": analysis_type
        })
        
        if result.get("isError"):
            return {
                "type": "error",
                "message": f"❌ Analysis failed: {result}",
                "timestamp": timestamp,
                "user": "System"
            }
        
        content = result["content"][0]["text"]
        analysis_result = json.loads(content)
        
        # Format result nicely
        formatted_result = format_analysis_result(analysis_result, len(data))
        
        return {
            "type": "analysis",
            "message": formatted_result,
            "timestamp": timestamp,
            "user": "System",
            "data": analysis_result
        }
    except Exception as e:
        return {
            "type": "error",
            "message": f"❌ Analysis error: {str(e)}",
            "timestamp": timestamp,
            "user": "System"
        }

async def handle_notify_command(parts: List[str], timestamp: str) -> Dict[str, Any]:
    """Handle notify command"""
    if len(parts) < 4:
        return {
            "type": "error",
            "message": "❌ **Usage**: `notify <channel> <recipient> <message>`\n\n**Examples**:\n• `notify slack #alerts System maintenance`\n• `notify email admin@example.com Critical alert`\n\n**Channels**: slack, email, webhook",
            "timestamp": timestamp,
            "user": "System"
        }
    
    channel = parts[1]
    recipient = parts[2]
    message = " ".join(parts[3:])
    
    if not manager.mcp_client:
        return {
            "type": "error",
            "message": "❌ MCP client not connected",
            "timestamp": timestamp,
            "user": "System"
        }
    
    try:
        result = await manager.mcp_client.call_tool("send_notification", {
            "channel": channel,
            "message": message,
            "recipient": recipient,
            "priority": "medium"
        })
        
        notification_result = json.loads(result["content"][0]["text"])
        
        return {
            "type": "notification",
            "message": f"✅ **Notification Sent**\n\n• **Channel**: {channel}\n• **Recipient**: {recipient}\n• **Status**: {notification_result.get('status', 'unknown')}\n• **ID**: {notification_result.get('notification_id', 'N/A')}",
            "timestamp": timestamp,
            "user": "System",
            "data": notification_result
        }
    except Exception as e:
        return {
            "type": "error",
            "message": f"❌ Notification error: {str(e)}",
            "timestamp": timestamp,
            "user": "System"
        }

async def handle_workflow_command(parts: List[str], timestamp: str) -> Dict[str, Any]:
    """Handle workflow command"""
    if len(parts) < 2:
        return {
            "type": "error",
            "message": "❌ **Usage**: `workflow <type>`\n\n**Types**:\n• `sample` - Run sample workflow\n• `analysis` - Data analysis workflow\n• `notification` - Notification workflow",
            "timestamp": timestamp,
            "user": "System"
        }
    
    workflow_type = parts[1]
    
    if not manager.mcp_client:
        return {
            "type": "error",
            "message": "❌ MCP client not connected",
            "timestamp": timestamp,
            "user": "System"
        }
    
    try:
        if workflow_type == "sample":
            workflow_steps = [
                {"step_type": "data_analysis", "parameters": {"data": [1,2,3,4,5], "analysis_type": "basic"}},
                {"step_type": "notification", "parameters": {"channel": "slack", "message": "Analysis complete", "recipient": "#alerts"}}
            ]
            
            result = await manager.mcp_client.call_tool("process_workflow", {
                "workflow_steps": workflow_steps,
                "trigger_condition": "manual_web_interface"
            })
            
            workflow_result = json.loads(result["content"][0]["text"])
            
            return {
                "type": "workflow",
                "message": f"✅ **Workflow Completed**\n\n• **ID**: {workflow_result['workflow_id']}\n• **Steps**: {workflow_result['total_steps']}\n• **Completed**: {workflow_result['completed_steps']}\n• **Failed**: {workflow_result['failed_steps']}\n• **Time**: {workflow_result.get('completion_time', 'N/A')}",
                "timestamp": timestamp,
                "user": "System",
                "data": workflow_result
            }
        
        elif workflow_type == "analysis":
            # Use sample data for analysis workflow
            data = [1200, 1350, 1100, 980, 1450, 1600, 1200, 1800, 1900, 2100]
            result = await manager.orchestrator.run_data_analysis_workflow(data)
            
            return {
                "type": "workflow",
                "message": f"✅ **Analysis Workflow Completed**\n\n• **ID**: {result['workflow_id']}\n• **Steps**: {len(result['steps'])}\n• **Data Points**: {len(data)}",
                "timestamp": timestamp,
                "user": "System",
                "data": result
            }
        
        else:
            return {
                "type": "error",
                "message": f"❌ Unknown workflow type: **{workflow_type}**",
                "timestamp": timestamp,
                "user": "System"
            }
    except Exception as e:
        return {
            "type": "error",
            "message": f"❌ Workflow error: {str(e)}",
            "timestamp": timestamp,
            "user": "System"
        }

async def handle_resource_command(parts: List[str], timestamp: str) -> Dict[str, Any]:
    """Handle resource command"""
    if len(parts) < 2:
        return {
            "type": "error",
            "message": "❌ **Usage**: `resource <uri>`\n\n**Available Resources**:\n• `data://analytics/dashboard`\n• `config://server/settings`\n• `logs://system/recent`",
            "timestamp": timestamp,
            "user": "System"
        }
    
    uri = parts[1]
    
    if not manager.mcp_client:
        return {
            "type": "error",
            "message": "❌ MCP client not connected",
            "timestamp": timestamp,
            "user": "System"
        }
    
    try:
        result = await manager.mcp_client.get_resource(uri)
        content = result["contents"][0]["text"]
        
        # Try to parse as JSON for pretty printing
        try:
            data = json.loads(content)
            formatted_content = f"📁 **Resource**: {uri}\n\n```json\n{json.dumps(data, indent=2)}\n```"
        except json.JSONDecodeError:
            formatted_content = f"📁 **Resource**: {uri}\n\n```\n{content}\n```"
        
        return {
            "type": "resource",
            "message": formatted_content,
            "timestamp": timestamp,
            "user": "System",
            "data": {"uri": uri, "content": content}
        }
    except Exception as e:
        return {
            "type": "error",
            "message": f"❌ Resource error: {str(e)}",
            "timestamp": timestamp,
            "user": "System"
        }

async def handle_sample_command(parts: List[str], timestamp: str) -> Dict[str, Any]:
    """Handle sample command for demo purposes"""
    sample_type = parts[1] if len(parts) > 1 else "data"
    
    if sample_type == "data":
        sample_data = {
            "sales_q1": [1200, 1350, 1100],
            "sales_q2": [980, 1450, 1600],
            "sales_q3": [1200, 1800, 1900],
            "sales_q4": [2100, 2300, 2500]
        }
        
        return {
            "type": "sample",
            "message": f"📊 **Sample Data**\n\n```json\n{json.dumps(sample_data, indent=2)}\n```\n\n💡 **Try**: `analyze basic 1200,1350,1100,980,1450`",
            "timestamp": timestamp,
            "user": "System",
            "data": sample_data
        }
    
    elif sample_type == "commands":
        commands = [
            "analyze basic 1,2,3,4,5",
            "analyze statistical sample",
            "notify slack #alerts Test message",
            "workflow sample",
            "resource data://analytics/dashboard",
            "status"
        ]
        
        commands_text = "🎯 **Sample Commands**\n\n"
        for i, cmd in enumerate(commands, 1):
            commands_text += f"{i}. `{cmd}`\n"
        
        return {
            "type": "sample",
            "message": commands_text,
            "timestamp": timestamp,
            "user": "System",
            "data": commands
        }
    
    else:
        return {
            "type": "error",
            "message": "❌ **Usage**: `sample <type>`\n\n**Types**: data, commands",
            "timestamp": timestamp,
            "user": "System"
        }

async def get_help_text() -> str:
    """Get comprehensive help text"""
    return """
📋 **MCP Advanced Interface - Help**

🔧 **Basic Commands:**
• `help` - Show this help
• `status` - Show system status
• `tools` - List available tools

📊 **Data Analysis:**
• `analyze <type> <data>` - Analyze data
  - **Types**: basic, statistical, correlation, trend
  - **Data**: comma-separated numbers or 'sample'
  - **Examples**: 
    - `analyze basic 1,2,3,4,5`
    - `analyze statistical sample`
    - `analyze trend 1,3,2,4,5,7,6,8`

📢 **Notifications:**
• `notify <channel> <recipient> <message>`
  - **Channels**: slack, email, webhook
  - **Example**: `notify slack #alerts System maintenance`

🔄 **Workflows:**
• `workflow sample` - Run sample workflow
• `workflow analysis` - Data analysis workflow
• `workflow notification` - Notification workflow

📁 **Resources:**
• `resource <uri>` - Get resource content
  - **URIs**: 
    - `data://analytics/dashboard`
    - `config://server/settings`
    - `logs://system/recent`

🎯 **Samples:**
• `sample data` - Show sample datasets
• `sample commands` - Show example commands

💡 **Tips:**
- Commands are case-insensitive
- Use 'sample' as data for pre-loaded datasets
- Check status with `status` command
- All results are formatted with syntax highlighting

👤 **Current User**: AdilzhanB
📅 **Server Time**: 2025-06-16 13:46:16 UTC
"""

def format_analysis_result(result: Dict[str, Any], data_count: int) -> str:
    """Format analysis results for display"""
    analysis_type = result.get('analysis_type', 'unknown')
    
    formatted = f"📈 **Analysis Results ({analysis_type})**\n"
    formatted += f"📊 **Dataset**: {data_count} data points\n\n"
    
    # Group related metrics
    basic_metrics = ["count", "sum", "mean", "median", "min", "max", "range"]
    statistical_metrics = ["standard_deviation", "variance", "coefficient_of_variation"]
    trend_metrics = ["trend_slope", "trend_intercept", "r_squared", "trend_strength"]
    
    for key, value in result.items():
        if key == "analysis_type":
            continue
        elif isinstance(value, dict):
            formatted += f"**{key.replace('_', ' ').title()}:**\n"
            for k, v in value.items():
                if isinstance(v, float):
                    formatted += f"  • {k}: {v:.3f}\n"
                else:
                    formatted += f"  • {k}: {v}\n"
            formatted += "\n"
        elif isinstance(value, (int, float)):
            if key in basic_metrics:
                emoji = "📊"
            elif key in statistical_metrics:
                emoji = "📉"
            elif key in trend_metrics:
                emoji = "📈"
            else:
                emoji = "•"
            formatted += f"{emoji} **{key.replace('_', ' ').title()}**: {value:.3f}\n"
        elif isinstance(value, list):
            if key == "forecast_next_3":
                formatted += f"🔮 **{key.replace('_', ' ').title()}**: {', '.join([f'{x:.2f}' for x in value])}\n"
            else:
                formatted += f"• **{key.replace('_', ' ').title()}**: {', '.join(map(str, value))}\n"
        else:
            formatted += f"• **{key.replace('_', ' ').title()}**: {value}\n"
    
    return formatted

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 MCP Web Service starting up...")
    logger.info(f"📅 Server time: 2025-06-16 13:46:16 UTC")
    logger.info(f"👤 Default user: AdilzhanB")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 MCP Web Service shutting down...")
    if manager.mcp_client:
        await manager.mcp_client.disconnect()

if __name__ == "__main__":
    uvicorn.run(
        "web_service.app:app",
        host=os.getenv("WEB_HOST", "0.0.0.0"),
        port=int(os.getenv("WEB_PORT", "8000")),
        reload=os.getenv("WEB_RELOAD", "true").lower() == "true",
        log_level="info"
    )