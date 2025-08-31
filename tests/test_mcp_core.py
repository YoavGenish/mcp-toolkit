"""
Core MCP functionality tests.
"""

import pytest
import json
import logging
from mcp import MCP


class TestMCPCore:
    """Test core MCP functionality."""

    def test_mcp_initialization(self):
        """Test MCP server initialization."""
        server = MCP("Test Server", "1.0.0")
        
        assert server.server_name == "Test Server"
        assert server.server_version == "1.0.0"
        assert not server.initialized
        assert len(server.tools) == 0

    def test_mcp_initialization_with_logging_disabled(self):
        """Test MCP server initialization with logging disabled."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        assert server.server_name == "Test Server"
        assert not server.enable_logging
        assert server.logger.level > logging.CRITICAL

    def test_tool_registration(self):
        """Test tool registration functionality."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({
            "Title": "Test Tool",
            "Description": "A test tool"
        })
        def test_func(param1: str, param2: int = 42) -> str:
            """Test function.
            
            param1: First parameter
            param2: Second parameter
            """
            return f"{param1}-{param2}"
        
        assert len(server.tools) == 1
        assert "test_func" in server.tools
        
        tool_info = server.tools["test_func"]
        assert tool_info["title"] == "Test Tool"
        assert tool_info["description"] == "A test tool"
        assert tool_info["function"].__name__ == test_func.__name__
        assert "param1" in tool_info["required_params"]
        assert "param2" not in tool_info["required_params"]  # Has default value
        
        # Test properties
        properties = tool_info["properties"]
        assert properties["param1"]["type"] == "string"
        assert properties["param2"]["type"] == "integer"

    def test_list_tools(self):
        """Test listing registered tools."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Tool 1", "Description": "First tool"})
        def tool1():
            return "tool1"
        
        @server.add({"Title": "Tool 2", "Description": "Second tool"})
        def tool2():
            return "tool2"
        
        tools = server.list_tools()
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools

    def test_initialize_request(self):
        """Test MCP initialize request handling."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"},
            "id": "init"
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "init"
        assert "result" in response
        
        result = response["result"]
        assert result["protocolVersion"] == "2024-11-05"
        assert "capabilities" in result
        assert "serverInfo" in result
        assert result["serverInfo"]["name"] == "Test Server"
        assert result["serverInfo"]["version"] == "1.0.0"
        assert server.initialized

    def test_tools_list_request(self):
        """Test tools/list request handling."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Test Tool", "Description": "A test tool"})
        def test_func(param: str) -> str:
            """Test function.
            
            param: A parameter
            """
            return param
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": "list"
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "list"
        assert "result" in response
        
        result = response["result"]
        assert "tools" in result
        assert len(result["tools"]) == 1
        
        tool = result["tools"][0]
        assert tool["name"] == "test_func"
        assert tool["description"] == "A test tool"
        assert "inputSchema" in tool
        assert tool["inputSchema"]["type"] == "object"
        assert "param" in tool["inputSchema"]["properties"]

    def test_tools_call_request(self):
        """Test tools/call request handling."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Add", "Description": "Add two numbers"})
        def add(x: int, y: int) -> int:
            """Add two numbers.
            
            x: First number
            y: Second number
            """
            return x + y
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "add",
                "arguments": {"x": 5, "y": 3}
            },
            "id": "call"
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "call"
        assert "result" in response
        
        result = response["result"]
        assert "content" in result
        assert len(result["content"]) == 1
        assert result["content"][0]["type"] == "text"
        assert result["content"][0]["text"] == "8"

    def test_logging_control(self):
        """Test logging enable/disable functionality."""
        server = MCP("Test Server", "1.0.0", enable_logging=True)
        
        # Initially enabled
        assert server.enable_logging
        
        # Disable logging
        server.enable_logs(False)
        assert not server.enable_logging
        
        # Re-enable logging
        server.enable_logs(True)
        assert server.enable_logging

    def test_set_log_level(self):
        """Test setting log level."""
        server = MCP("Test Server", "1.0.0", enable_logging=True)
        
        # Set to DEBUG level
        server.set_log_level(logging.DEBUG)
        assert server.logger.level == logging.DEBUG
        
        # Set to WARNING level
        server.set_log_level(logging.WARNING)
        assert server.logger.level == logging.WARNING