"""
MCP Advanced Client Package

This package provides client implementations for connecting to and
interacting with MCP servers, including CLI and workflow orchestration.

Created by: AdilzhanB
Date: 2025-06-17 04:41:53 UTC
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AdilzhanB"
__email__ = "baidalin_adilzhan.2010@mail.ru"
__description__ = "Model Context Protocol Client Implementation"
__license__ = "MIT"
__created__ = "2025-06-17T04:41:53Z"

from .mcp_client import MCPClient, WorkflowOrchestrator

__all__ = [
    "MCPClient",
    "WorkflowOrchestrator"
]

# Package metadata
PACKAGE_INFO = {
    "name": "mcp-advanced-client",
    "version": __version__,
    "author": __author__,
    "description": __description__,
    "license": __license__,
    "created": __created__,
    "features": [
        "mcp_client_connection",
        "tool_calling",
        "resource_access",
        "prompt_management",
        "workflow_orchestration",
        "cli_interface"
    ],
    "supported_interfaces": [
        "command_line",
        "programmatic_api",
        "workflow_orchestration"
    ]
}

def get_client_info():
    """Get client package information"""
    return PACKAGE_INFO.copy()

def create_client(server_command=None):
    """Create a new MCP client instance
    
    Args:
        server_command: Command to start the MCP server
        
    Returns:
        MCPClient: Configured client instance
    """
    if server_command is None:
        server_command = ["python", "server/main.py"]
    
    return MCPClient(server_command)

def create_orchestrator(client):
    """Create a workflow orchestrator
    
    Args:
        client: MCPClient instance
        
    Returns:
        WorkflowOrchestrator: Configured orchestrator
    """
    return WorkflowOrchestrator(client)

# Logging configuration
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler if none exists
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

logger.info(f"MCP Advanced Client v{__version__} initialized by {__author__}")