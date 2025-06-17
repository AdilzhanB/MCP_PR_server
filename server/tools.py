"""
MCP Server Tools Implementation
"""

import asyncio
import json
import statistics
from typing import Any, Dict, List, Optional
import aiohttp
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataAnalyzer:
    """Advanced data analysis tool"""
    
    async def analyze(self, data: List[float], analysis_type: str) -> Dict[str, Any]:
        """Perform data analysis based on type"""
        if not data:
            return {"error": "No data provided"}
            
        try:
            if analysis_type == "basic":
                return await self._basic_analysis(data)
            elif analysis_type == "statistical":
                return await self._statistical_analysis(data)
            elif analysis_type == "correlation":
                return await self._correlation_analysis(data)
            elif analysis_type == "trend":
                return await self._trend_analysis(data)
            else:
                return {"error": f"Unknown analysis type: {analysis_type}"}
        except Exception as e:
            logger.error(f"Data analysis error: {e}")
            return {"error": str(e)}
    
    async def _basic_analysis(self, data: List[float]) -> Dict[str, Any]:
        """Basic statistical analysis"""
        return {
            "count": len(data),
            "sum": sum(data),
            "mean": statistics.mean(data),
            "median": statistics.median(data),
            "min": min(data),
            "max": max(data),
            "range": max(data) - min(data),
            "analysis_type": "basic"
        }
    
    async def _statistical_analysis(self, data: List[float]) -> Dict[str, Any]:
        """Advanced statistical analysis"""
        basic = await self._basic_analysis(data)
        
        try:
            stdev = statistics.stdev(data) if len(data) > 1 else 0
            variance = statistics.variance(data) if len(data) > 1 else 0
            
            # Calculate percentiles
            sorted_data = sorted(data)
            n = len(sorted_data)
            
            percentiles = {
                "25th": sorted_data[int(0.25 * n)] if n > 4 else sorted_data[0],
                "50th": statistics.median(data),
                "75th": sorted_data[int(0.75 * n)] if n > 4 else sorted_data[-1],
                "90th": sorted_data[int(0.9 * n)] if n > 10 else sorted_data[-1],
                "95th": sorted_data[int(0.95 * n)] if n > 20 else sorted_data[-1]
            }
            
            return {
                **basic,
                "standard_deviation": stdev,
                "variance": variance,
                "percentiles": percentiles,
                "coefficient_of_variation": (stdev / basic["mean"]) * 100 if basic["mean"] != 0 else 0,
                "analysis_type": "statistical"
            }
        except Exception as e:
            return {**basic, "error": f"Statistical analysis error: {e}"}
    
    async def _correlation_analysis(self, data: List[float]) -> Dict[str, Any]:
        """Correlation and relationship analysis"""
        basic = await self._basic_analysis(data)
        
        # Create indices for correlation with position
        indices = list(range(len(data)))
        
        try:
            # Calculate correlation with position (trend indicator)
            correlation = np.corrcoef(indices, data)[0, 1] if len(data) > 1 else 0
            
            # Calculate autocorrelation (lag-1)
            autocorr = 0
            if len(data) > 2:
                lag1_pairs = [(data[i], data[i+1]) for i in range(len(data)-1)]
                x_vals = [pair[0] for pair in lag1_pairs]
                y_vals = [pair[1] for pair in lag1_pairs]
                autocorr = np.corrcoef(x_vals, y_vals)[0, 1]
            
            return {
                **basic,
                "position_correlation": correlation,
                "autocorrelation_lag1": autocorr,
                "trend_direction": "increasing" if correlation > 0.1 else "decreasing" if correlation < -0.1 else "stable",
                "analysis_type": "correlation"
            }
        except Exception as e:
            return {**basic, "error": f"Correlation analysis error: {e}"}
    
    async def _trend_analysis(self, data: List[float]) -> Dict[str, Any]:
        """Trend analysis with forecasting"""
        basic = await self._basic_analysis(data)
        
        try:
            # Simple linear regression for trend
            n = len(data)
            x = np.array(range(n))
            y = np.array(data)
            
            # Calculate slope and intercept
            x_mean = np.mean(x)
            y_mean = np.mean(y)
            
            slope = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2) if n > 1 else 0
            intercept = y_mean - slope * x_mean
            
            # Calculate R-squared
            y_pred = slope * x + intercept
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - y_mean) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Simple forecast for next 3 points
            forecast = [slope * (n + i) + intercept for i in range(1, 4)]
            
            return {
                **basic,
                "trend_slope": slope,
                "trend_intercept": intercept,
                "r_squared": r_squared,
                "trend_strength": "strong" if abs(r_squared) > 0.7 else "moderate" if abs(r_squared) > 0.3 else "weak",
                "forecast_next_3": forecast,
                "analysis_type": "trend"
            }
        except Exception as e:
            return {**basic, "error": f"Trend analysis error: {e}"}

class WebhookManager:
    """Webhook management and triggering"""
    
    def __init__(self):
        self.webhooks = {}
    
    async def setup_webhook(self, endpoint: str, events: List[str], secret: Optional[str] = None) -> Dict[str, Any]:
        """Setup a new webhook"""
        webhook_id = f"webhook_{len(self.webhooks) + 1}"
        
        webhook_config = {
            "id": webhook_id,
            "endpoint": endpoint,
            "events": events,
            "secret": secret,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.webhooks[webhook_id] = webhook_config
        
        logger.info(f"Webhook {webhook_id} setup for endpoint {endpoint}")
        
        return {
            "webhook_id": webhook_id,
            "status": "created",
            "endpoint": endpoint,
            "events": events
        }
    
    async def trigger_webhook(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger a webhook with payload"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "MCP-Server/1.0"
                }
                
                async with session.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_text = await response.text()
                    
                    return {
                        "status": "success",
                        "response_code": response.status,
                        "response_body": response_text[:500],  # Truncate long responses
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception as e:
            logger.error(f"Webhook trigger error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

class NotificationSender:
    """Multi-channel notification sender"""
    
    async def send(self, channel: str, message: str, recipient: str, priority: str = "medium") -> Dict[str, Any]:
        """Send notification via specified channel"""
        notification_id = f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            if channel == "slack":
                return await self._send_slack(notification_id, message, recipient, priority)
            elif channel == "email":
                return await self._send_email(notification_id, message, recipient, priority)
            elif channel == "webhook":
                return await self._send_webhook(notification_id, message, recipient, priority)
            else:
                return {
                    "notification_id": notification_id,
                    "status": "error",
                    "error": f"Unknown channel: {channel}"
                }
        except Exception as e:
            logger.error(f"Notification send error: {e}")
            return {
                "notification_id": notification_id,
                "status": "error",
                "error": str(e)
            }
    
    async def _send_slack(self, notification_id: str, message: str, recipient: str, priority: str) -> Dict[str, Any]:
        """Send Slack notification (simulated)"""
        # In a real implementation, this would use Slack API
        await asyncio.sleep(0.1)  # Simulate API delay
        
        return {
            "notification_id": notification_id,
            "channel": "slack",
            "status": "sent",
            "recipient": recipient,
            "message_length": len(message),
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _send_email(self, notification_id: str, message: str, recipient: str, priority: str) -> Dict[str, Any]:
        """Send email notification (simulated)"""
        # In a real implementation, this would use SMTP or email service API
        await asyncio.sleep(0.2)  # Simulate email send delay
        
        return {
            "notification_id": notification_id,
            "channel": "email",
            "status": "sent",
            "recipient": recipient,
            "subject": f"[{priority.upper()}] MCP Notification",
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _send_webhook(self, notification_id: str, message: str, recipient: str, priority: str) -> Dict[str, Any]:
        """Send webhook notification"""
        payload = {
            "notification_id": notification_id,
            "message": message,
            "recipient": recipient,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    recipient,  # recipient is webhook URL
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return {
                        "notification_id": notification_id,
                        "channel": "webhook",
                        "status": "sent",
                        "response_code": response.status,
                        "timestamp": datetime.now().isoformat()
                    }
        except Exception as e:
            return {
                "notification_id": notification_id,
                "channel": "webhook",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }