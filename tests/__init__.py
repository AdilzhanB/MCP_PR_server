"""
MCP Advanced Project Test Suite

This package contains comprehensive tests for the MCP server, client,
and web service components.

Created by: AdilzhanB
Date: 2025-06-17 04:41:53 UTC
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AdilzhanB"
__email__ = "baidalin_adilzhan.2010@mail.ru"
__description__ = "Test Suite for MCP Advanced Project"
__license__ = "MIT"
__created__ = "2025-06-17T04:41:53Z"

import pytest
import asyncio
import logging
from pathlib import Path

__all__ = [
    "run_all_tests",
    "run_server_tests",
    "run_client_tests", 
    "run_web_service_tests",
    "TEST_CONFIG"
]

# Test configuration
TEST_CONFIG = {
    "test_data_dir": Path(__file__).parent / "test_data",
    "temp_dir": Path(__file__).parent / "temp",
    "log_level": "DEBUG",
    "timeout": 30,
    "coverage_min": 80,
    "test_categories": [
        "unit",
        "integration",
        "web",
        "asyncio",
        "slow"
    ]
}

# Sample test data
SAMPLE_TEST_DATA = {
    "basic_data": [1.0, 2.0, 3.0, 4.0, 5.0],
    "statistical_data": [1.2, 2.3, 1.8, 3.1, 2.7, 4.2, 3.8, 2.9, 3.5, 4.1],
    "trend_data": [10, 12, 11, 15, 18, 16, 20, 22, 19, 25, 28, 26],
    "large_dataset": list(range(1, 101)),
    "edge_cases": {
        "empty": [],
        "single": [42.0],
        "negative": [-5, -3, -1, 2, 4],
        "zeros": [0, 0, 0, 1, 2],
        "duplicates": [1, 1, 2, 2, 3, 3]
    }
}

def get_test_data(dataset_name="basic_data"):
    """Get test data by name
    
    Args:
        dataset_name: Name of the dataset to retrieve
        
    Returns:
        List or dict of test data
    """
    return SAMPLE_TEST_DATA.get(dataset_name, SAMPLE_TEST_DATA["basic_data"])

def run_all_tests():
    """Run all test suites"""
    test_args = [
        "tests/",
        "-v",
        "--cov=server",
        "--cov=client", 
        "--cov=web_service",
        f"--cov-fail-under={TEST_CONFIG['coverage_min']}",
        "--tb=short",
        "--durations=10"
    ]
    
    return pytest.main(test_args)

def run_server_tests():
    """Run server-specific tests"""
    return pytest.main([
        "tests/test_server.py",
        "-v",
        "-m", "not slow"
    ])

def run_client_tests():
    """Run client-specific tests"""
    return pytest.main([
        "tests/test_client.py",
        "-v",
        "-m", "not slow"
    ])

def run_web_service_tests():
    """Run web service tests"""
    return pytest.main([
        "tests/test_web_service.py",
        "-v",
        "-m", "not slow"
    ])

# Test utilities
class TestBase:
    """Base class for test cases"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method run before each test"""
        self.test_start_time = "2025-06-17T04:41:53Z"
        self.test_user = "AdilzhanB"
        
        # Create temp directory if it doesn't exist
        TEST_CONFIG["temp_dir"].mkdir(exist_ok=True)
    
    def get_sample_data(self, size="small"):
        """Get sample data for testing
        
        Args:
            size: Size of dataset ('small', 'medium', 'large')
            
        Returns:
            List of sample data
        """
        if size == "small":
            return get_test_data("basic_data")
        elif size == "medium":
            return get_test_data("statistical_data")
        elif size == "large":
            return get_test_data("large_dataset")
        else:
            return get_test_data()

# Async test utilities
def async_test(coro):
    """Decorator for async test functions"""
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper

# Mock utilities
class MockMCPClient:
    """Mock MCP client for testing"""
    
    def __init__(self):
        self.connected = False
        self.call_count = 0
    
    async def connect(self):
        self.connected = True
    
    async def disconnect(self):
        self.connected = False
    
    async def call_tool(self, name, arguments):
        self.call_count += 1
        return {
            "content": [{"text": '{"mock": "response"}'}],
            "isError": False
        }

# Logging configuration for tests
logging.basicConfig(
    level=getattr(logging, TEST_CONFIG["log_level"]),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"MCP Test Suite v{__version__} initialized by {__author__} at {__created__}")