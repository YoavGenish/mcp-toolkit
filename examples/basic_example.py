"""
Basic example showing the core functionality of mcp-lite.
Run with: python basic_example.py
"""

import json
from mcp import MCP

def main():
    """Demonstrate basic MCP functionality."""
    
    # Create MCP server instance
    server = MCP("Basic MCP Server", "1.0.0")
    
    # Register some example tools
    @server.add({
        "Title": "Add Numbers",
        "Description": "Add two numbers together"
    })
    def add(x: int, y: int) -> int:
        """Add two numbers.
        
        x: First number
        y: Second number
        """
        return x + y
    
    @server.add({
        "Title": "String Info",
        "Description": "Get information about a string"
    })
    def string_info(text: str) -> dict:
        """Get string information.
        
        text: String to analyze
        """
        return {
            "length": len(text),
            "upper": text.upper(),
            "lower": text.lower(),
            "word_count": len(text.split()),
            "is_numeric": text.isdigit(),
            "is_alpha": text.isalpha()
        }
    
    @server.add({
        "Title": "List Operations",
        "Description": "Perform operations on a list of numbers"
    })
    def list_operations(numbers: list, operation: str = "sum") -> float:
        """Perform operations on a list of numbers.
        
        numbers: List of numbers to process
        operation: Operation to perform (sum, average, max, min)
        """
        if not numbers:
            return 0
        
        if operation == "sum":
            return sum(numbers)
        elif operation == "average":
            return sum(numbers) / len(numbers)
        elif operation == "max":
            return max(numbers)
        elif operation == "min":
            return min(numbers)
        else:
            return sum(numbers)  # Default to sum
    
    print("=== MCP Lite Basic Example ===")
    print(f"Server: {server.server_name} v{server.server_version}")
    print(f"Available tools: {server.list_tools()}")
    print()
    
    # Test different MCP requests
    test_requests = [
        # Initialize the server
        {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"},
            "id": "init"
        },
        
        # List available tools
        {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": "list"
        },
        
        # Call the add function
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "add",
                "arguments": {"x": 10, "y": 25}
            },
            "id": "add_call"
        },
        
        # Call string_info function
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "string_info",
                "arguments": {"text": "Hello MCP World!"}
            },
            "id": "string_call"
        },
        
        # Call list_operations function
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "list_operations",
                "arguments": {
                    "numbers": [1, 2, 3, 4, 5],
                    "operation": "average"
                }
            },
            "id": "list_call"
        }
    ]
    
    # Process each request and show results
    for i, request in enumerate(test_requests, 1):
        print(f"--- Request {i}: {request['method']} ---")
        print(f"Request: {json.dumps(request, indent=2)}")
        
        response = server.run(request)
        print(f"Response: {json.dumps(response, indent=2)}")
        print()
    
    # Demonstrate error handling
    print("--- Error Handling Example ---")
    error_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "add",
            "arguments": {"x": 10}  # Missing required parameter 'y'
        },
        "id": "error_test"
    }
    
    print(f"Request with missing parameter:")
    print(f"Request: {json.dumps(error_request, indent=2)}")
    
    error_response = server.run(error_request)
    print(f"Error Response: {json.dumps(error_response, indent=2)}")

if __name__ == "__main__":
    main()