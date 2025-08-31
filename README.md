# MCP Lite

A lightweight, decorator-based Python library for implementing the Model Context Protocol (MCP). Transform your Python functions into MCP-compatible tools with minimal code.

## Features

- **Decorator-based**: Register functions as MCP tools with simple decorators
- **Transport agnostic**: Works with Flask, FastAPI, Lambda, Django, or any Python web framework
- **Type inference**: Automatically generates JSON schemas from function signatures and type hints
- **Zero dependencies**: Pure Python with only standard library imports
- **MCP compliant**: Full support for MCP protocol specification

## Installation

```bash
pip install mcp-lite
```

## Quick Start

```python
from mcp import MCP
import json

# Create an MCP instance
server = MCP("My Server", "1.0.0")

# Register tools with decorators
@server.add({
    "Title": "Add Numbers", 
    "Description": "Add two numbers together"
})
def add(x: int, y: int) -> int:
    """Add two numbers.
    
    x: First number to add
    y: Second number to add
    """
    return x + y

# Handle MCP requests
request = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {"name": "add", "arguments": {"x": 5, "y": 3}},
    "id": 1
}

response = server.run(request)
print(json.dumps(response, indent=2))
```

## License

MIT License - see LICENSE file for details.