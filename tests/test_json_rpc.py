"""
JSON-RPC protocol tests.
"""

import pytest
import json
from mcp import MCP


class TestJSONRPC:
    """Test JSON-RPC protocol compliance."""

    def test_valid_json_rpc_request(self):
        """Test handling of valid JSON-RPC 2.0 requests."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Test", "Description": "Test function"})
        def test_func():
            """Test function."""
            return "success"
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "test_func", "arguments": {}},
            "id": 123
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 123
        assert "result" in response
        assert "error" not in response

    def test_json_rpc_request_as_string(self):
        """Test handling JSON-RPC request as JSON string."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Test", "Description": "Test function"})
        def test_func():
            """Test function."""
            return "success"
        
        request_str = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "test_func", "arguments": {}},
            "id": "string-id"
        })
        
        response = server.run(request_str)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "string-id"
        assert "result" in response

    def test_missing_jsonrpc_version(self):
        """Test error handling for missing jsonrpc version."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        request = {
            "method": "test_method",
            "params": {},
            "id": 1
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "id" not in response or response["id"] is None
        assert "error" in response
        assert response["error"]["code"] == -32600
        assert "Invalid Request" in response["error"]["message"]

    def test_invalid_jsonrpc_version(self):
        """Test error handling for invalid jsonrpc version."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        request = {
            "jsonrpc": "1.0",  # Wrong version
            "method": "test_method",
            "params": {},
            "id": 1
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "id" not in response or response["id"] is None
        assert "error" in response
        assert response["error"]["code"] == -32600

    def test_missing_method(self):
        """Test error handling for missing method."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        request = {
            "jsonrpc": "2.0",
            "params": {},
            "id": 1
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32600
        assert "Missing method" in response["error"]["message"] or "Invalid Request" in response["error"]["message"]

    def test_method_not_found(self):
        """Test error handling for unknown method."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        request = {
            "jsonrpc": "2.0",
            "method": "unknown_method",
            "params": {},
            "id": 1
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32601
        assert "Method not found" in response["error"]["message"]

    def test_invalid_json(self):
        """Test error handling for invalid JSON."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        # Invalid JSON string
        invalid_json = '{"jsonrpc": "2.0", "method": "test", "id": 1'  # Missing closing brace
        
        response = server.run(invalid_json)
        
        assert response["jsonrpc"] == "2.0"
        assert "id" not in response or response["id"] is None
        assert "error" in response
        assert response["error"]["code"] == -32700
        assert "Parse error" in response["error"]["message"]

    def test_request_without_id(self):
        """Test handling request without id (notification)."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Test", "Description": "Test function"})
        def test_func():
            """Test function."""
            return "success"
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "test_func", "arguments": {}}
            # No "id" field
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert "id" not in response or response["id"] is None
        assert "result" in response

    def test_params_optional(self):
        """Test that params field is optional."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1
            # No "params" field
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response

    def test_error_response_structure(self):
        """Test that error responses have correct structure."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        request = {
            "jsonrpc": "2.0",
            "method": "nonexistent_method",
            "params": {},
            "id": 42
        }
        
        response = server.run(request)
        
        # Check JSON-RPC error response structure
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 42
        assert "error" in response
        assert "result" not in response
        
        error = response["error"]
        assert "code" in error
        assert "message" in error
        assert isinstance(error["code"], int)
        assert isinstance(error["message"], str)

    def test_success_response_structure(self):
        """Test that success responses have correct structure."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Test", "Description": "Test function"})
        def test_func():
            """Test function."""
            return {"result": "success"}
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "test_func", "arguments": {}},
            "id": 42
        }
        
        response = server.run(request)
        
        # Check JSON-RPC success response structure
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 42
        assert "result" in response
        assert "error" not in response

    def test_mcp_protocol_methods(self):
        """Test MCP-specific protocol methods."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        # Test initialize
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"},
            "id": 1
        }
        
        response = server.run(init_request)
        assert "result" in response
        assert "protocolVersion" in response["result"]
        
        # Test initialized notification
        init_notif = {
            "jsonrpc": "2.0",
            "method": "initialized",
            "id": 2
        }
        
        response = server.run(init_notif)
        assert "result" in response
        
        # Test tools/list
        list_request = {
            "jsonrpc": "2.0", 
            "method": "tools/list",
            "params": {},
            "id": 3
        }
        
        response = server.run(list_request)
        assert "result" in response
        assert "tools" in response["result"]