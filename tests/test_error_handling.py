"""
Error handling tests.
"""

import pytest
from mcp import MCP


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_missing_required_parameters(self):
        """Test error when required parameters are missing."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Test", "Description": "Test function"})
        def test_func(required_param: str, optional_param: str = "default"):
            """Test function.
            
            required_param: Required parameter
            optional_param: Optional parameter
            """
            return f"{required_param}-{optional_param}"
        
        # Request missing required parameter
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "test_func",
                "arguments": {"optional_param": "test"}  # Missing required_param
            },
            "id": 1
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32602
        assert "Invalid params" in response["error"]["message"]
        assert "required_param" in response["error"]["data"]

    def test_tool_execution_exception(self):
        """Test error handling when tool execution raises exception."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Failing Function", "Description": "Function that fails"})
        def failing_func():
            """Function that raises an exception."""
            raise ValueError("Something went wrong!")
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "failing_func", "arguments": {}},
            "id": 1
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Internal error" in response["error"]["message"]
        assert "Something went wrong!" in response["error"]["data"]

    def test_nonexistent_tool_in_tools_call(self):
        """Test error when calling nonexistent tool via tools/call."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "nonexistent_tool", "arguments": {}},
            "id": 1
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32601
        assert "Method not found" in response["error"]["message"]
        assert "nonexistent_tool" in response["error"]["data"]

    def test_missing_tool_name_in_tools_call(self):
        """Test error when tool name is missing in tools/call."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"arguments": {}},  # Missing "name"
            "id": 1
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32602
        assert "Invalid params" in response["error"]["message"]
        assert "Missing tool name" in response["error"]["data"]

    def test_direct_tool_call_missing_params(self):
        """Test direct tool call with missing parameters."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Test", "Description": "Test function"})
        def test_func(param1: str, param2: int):
            """Test function.
            
            param1: First parameter
            param2: Second parameter
            """
            return f"{param1}-{param2}"
        
        # Direct call to tool method (not via tools/call)
        request = {
            "jsonrpc": "2.0",
            "method": "test_func",
            "params": {"param1": "test"},  # Missing param2
            "id": 1
        }
        
        response = server.run(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "error" in response
        assert response["error"]["code"] == -32602
        assert "param2" in response["error"]["data"]

    def test_empty_arguments_in_tools_call(self):
        """Test tools/call with empty arguments for function with required params."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Test", "Description": "Test function"})
        def test_func(required: str):
            """Test function.
            
            required: Required parameter
            """
            return required
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "test_func",
                "arguments": {}  # Empty arguments
            },
            "id": 1
        }
        
        response = server.run(request)
        
        assert "error" in response
        assert response["error"]["code"] == -32602
        assert "required" in response["error"]["data"]

    def test_function_with_no_parameters_success(self):
        """Test that function with no parameters works correctly."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "No Params", "Description": "Function with no parameters"})
        def no_params_func():
            """Function with no parameters."""
            return "success"
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "no_params_func", "arguments": {}},
            "id": 1
        }
        
        response = server.run(request)
        
        assert "result" in response
        assert response["result"]["content"][0]["text"] == "success"

    def test_partial_parameters_provided(self):
        """Test with some required parameters missing."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Multiple Params", "Description": "Function with multiple parameters"})
        def multi_param_func(a: str, b: int, c: bool):
            """Function with multiple required parameters.
            
            a: String parameter
            b: Integer parameter  
            c: Boolean parameter
            """
            return f"{a}-{b}-{c}"
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call", 
            "params": {
                "name": "multi_param_func",
                "arguments": {"a": "test", "c": True}  # Missing "b"
            },
            "id": 1
        }
        
        response = server.run(request)
        
        assert "error" in response
        assert response["error"]["code"] == -32602
        assert "b" in response["error"]["data"]
        # The error message should mention missing parameters
        assert "Missing required parameters" in response["error"]["data"]

    def test_exception_preserves_request_id(self):
        """Test that exceptions preserve the original request ID."""
        server = MCP("Test Server", "1.0.0", enable_logging=False)
        
        @server.add({"Title": "Exception Test", "Description": "Throws exception"})
        def exception_func():
            """Function that throws exception."""
            raise RuntimeError("Test exception")
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": "exception_func", "arguments": {}},
            "id": "custom-id-123"
        }
        
        response = server.run(request)
        
        assert response["id"] == "custom-id-123"
        assert "error" in response