"""
Simple demo of mcp-lite library functionality.
"""

from mcp import MCP
import json

def main():
    print("=== MCP Lite Demo ===")
    
    # Create MCP server
    server = MCP("Demo Server", "1.0.0")
    
    # Register a simple tool
    @server.add({
        "Title": "Greet",
        "Description": "Generate a greeting message"
    })
    def greet(name: str) -> str:
        """Greet someone by name.
        
        name: Name of the person to greet
        """
        return f"Hello, {name}! Welcome to MCP Lite!"
    
    print(f"Server created: {server.server_name}")
    print(f"Available tools: {server.list_tools()}")
    
    # Test a simple request
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "greet",
            "arguments": {"name": "World"}
        },
        "id": 1
    }
    
    response = server.run(request)
    print(f"\nTest Response: {json.dumps(response, indent=2)}")
    
    print("\n🎉 MCP Lite is working!")
    print("Check the examples/ directory for more integration examples.")

if __name__ == "__main__":
    main()
