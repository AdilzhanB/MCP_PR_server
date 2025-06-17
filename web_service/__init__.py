"""
MCP Advanced Web Service Package

This package provides a FastAPI-based web interface for the MCP server,
including real-time WebSocket communication and REST API endpoints.

Created by: AdilzhanB
Date: 2025-06-17 04:41:53 UTC
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AdilzhanB"
__email__ = "baidalin_adilzhan.2010@mail.ru"
__description__ = "Web Interface for Model Context Protocol Server"
__license__ = "MIT"
__created__ = "2025-06-17T04:41:53Z"

from .app import app, manager

__all__ = [
    "app",
    "manager"
]

# Package metadata
PACKAGE_INFO = {
    "name": "mcp-advanced-web-service",
    "version": __version__,
    "author": __author__,
    "description": __description__,
    "license": __license__,
    "created": __created__,
    "features": [
        "web_chat_interface",
        "websocket_communication",
        "rest_api_endpoints",
        "real_time_updates",
        "responsive_design",
        "health_monitoring"
    ],
    "endpoints": [
        "/",
        "/api/health",
        "/api/tools",
        "/api/resources",
        "/api/analyze",
        "/ws"
    ],
    "technologies": [
        "FastAPI",
        "WebSockets",
        "Jinja2",
        "HTML5",
        "CSS3",
        "JavaScript"
    ]
}

def get_web_service_info():
    """Get web service package information"""
    return PACKAGE_INFO.copy()

def get_app():
    """Get the FastAPI application instance"""
    return app

def get_connection_manager():
    """Get the WebSocket connection manager"""
    return manager

# Configuration
DEFAULT_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
    "log_level": "info",
    "docs_url": "/api/docs",
    "redoc_url": "/api/redoc"
}

def get_default_config():
    """Get default web service configuration"""
    return DEFAULT_CONFIG.copy()

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

logger.info(f"MCP Advanced Web Service v{__version__} initialized by {__author__}")