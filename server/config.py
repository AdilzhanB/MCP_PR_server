"""
MCP Server Configuration
"""

import os
from typing import Dict, Any

class MCPConfig:
    """Configuration management for MCP server"""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables and defaults"""
        return {
            "server": {
                "name": os.getenv("MCP_SERVER_NAME", "advanced-mcp-server"),
                "version": "1.0.0",
                "debug": os.getenv("MCP_DEBUG", "false").lower() == "true",
                "log_level": os.getenv("MCP_LOG_LEVEL", "INFO")
            },
            "features": {
                "data_analysis": True,
                "webhooks": True,
                "notifications": True,
                "workflows": True
            },
            "limits": {
                "max_data_points": int(os.getenv("MCP_MAX_DATA_POINTS", "10000")),
                "max_workflow_steps": int(os.getenv("MCP_MAX_WORKFLOW_STEPS", "50")),
                "cache_ttl_seconds": int(os.getenv("MCP_CACHE_TTL", "300"))
            },
            "external_apis": {
                "slack_webhook_url": os.getenv("SLACK_WEBHOOK_URL"),
                "email_service_api": os.getenv("EMAIL_SERVICE_API"),
                "notification_timeout": int(os.getenv("NOTIFICATION_TIMEOUT", "10"))
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value