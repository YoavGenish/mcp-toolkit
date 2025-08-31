"""
Flask example showing how to integrate mcp-lite with Flask web framework.
Run with: python flask_example.py
"""

from flask import Flask, request, jsonify
from mcp import MCP

app = Flask(__name__)
mcp_server = MCP("Flask MCP Server", "1.0.0")

@mcp_server.add({
    "Title": "Echo Message",
    "Description": "Echo back the input message with a prefix"
})
def echo(message: str) -> str:
    """Echo back a message.
    
    message: The message to echo back
    """
    return f"Echo: {message}"

@mcp_server.add({
    "Title": "Calculate Area",
    "Description": "Calculate the area of a rectangle"
})
def calculate_area(width: float, height: float) -> float:
    """Calculate rectangle area.
    
    width: Width of the rectangle
    height: Height of the rectangle
    """
    return width * height

@mcp_server.add({
    "Title": "Get Server Info",
    "Description": "Get information about this Flask server"
})
def get_server_info() -> dict:
    """Get server information."""
    return {
        "server_type": "Flask",
        "mcp_version": "0.1.0",
        "available_tools": len(mcp_server.list_tools())
    }

@app.route('/mcp', methods=['POST'])
def handle_mcp():
    """Handle MCP requests via HTTP POST."""
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        response = mcp_server.run(request_data)
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/tools', methods=['GET'])
def list_tools():
    """Convenience endpoint to list available tools."""
    return jsonify({
        "tools": mcp_server.list_tools(),
        "server": "Flask MCP Server"
    })

@app.route('/')
def index():
    """Basic info page."""
    return """
    <h1>Flask MCP Server</h1>
    <p>MCP-Lite integration example</p>
    <ul>
        <li><a href="/tools">Available Tools</a></li>
        <li>POST to /mcp for MCP requests</li>
    </ul>
    """

if __name__ == '__main__':
    print("Starting Flask MCP Server...")
    print(f"Available tools: {mcp_server.list_tools()}")
    app.run(debug=True, port=8000)