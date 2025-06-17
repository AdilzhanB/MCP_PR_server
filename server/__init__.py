"""
MCP Advanced Server Package

This package contains the main MCP server implementation with advanced
features including data analysis, webhook management, notifications,
and workflow automation.

Created by: AdilzhanB
Date: 2025-06-17 04:41:53 UTC
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AdilzhanB"
__email__ = "baidalin_adilzhan.2010@mail.ru"
__description__ = "Advanced Model Context Protocol Server Implementation"
__license__ = "MIT"
__created__ = "2025-06-17T04:41:53Z"

from .main import AdvancedMCPServer
from .config import MCPConfig
from .tools import DataAnalyzer, WebhookManager, NotificationSender
from .resources import DataResourceManager

__all__ = [
    "AdvancedMCPServer",
    "MCPConfig",
    "DataAnalyzer",
    "WebhookManager", 
    "NotificationSender",
    "DataResourceManager"
]

# Package metadata
PACKAGE_INFO = {
    "name": "mcp-advanced-server",
    "version": __version__,
    "author": __author__,
    "description": __description__,
    "license": __license__,
    "created": __created__,
    "features": [
        "data_analysis",
        "webhook_management",
        "notifications",
        "workflow_automation",
        "resource_management"
    ],
    "supported_analysis_types": [
        "basic",
        "statistical",
        "correlation",
        "trend"
    ],
    "notification_channels": [
        "slack",
        "email",
        "webhook"
    ]
}

def get_server_info():
    """Get server package information"""
    return PACKAGE_INFO.copy()

def get_version():
    """Get current version"""
    return __version__

def get_author():
    """Get package author"""
    return __author__

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

logger.info(f"MCP Advanced Server v{__version__} initialized by {__author__}")