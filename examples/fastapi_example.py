"""
FastAPI example showing how to integrate mcp-lite with FastAPI.
Run with: uvicorn fastapi_example:app --reload --port 8001
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcp import MCP

app = FastAPI(title="FastAPI MCP Server", version="1.0.0")
mcp_server = MCP("FastAPI MCP Server", "1.0.0")

class MCPRequest(BaseModel):
    jsonrpc: str
    method: str
    params: dict = {}
    id: int | str | None = None

@mcp_server.add({
    "Title": "Greet User",
    "Description": "Generate a personalized greeting"
})
def greet(name: str, language: str = "en") -> str:
    """Greet a user in different languages.
    
    name: Name of the person to greet
    language: Language code (en, es, fr)
    """
    greetings = {
        "en": f"Hello, {name}!",
        "es": f"¡Hola, {name}!",
        "fr": f"Bonjour, {name}!"
    }
    return greetings.get(language, greetings["en"])

@mcp_server.add({
    "Title": "Calculate BMI",
    "Description": "Calculate Body Mass Index"
})
def calculate_bmi(weight_kg: float, height_m: float) -> dict:
    """Calculate BMI and category.
    
    weight_kg: Weight in kilograms
    height_m: Height in meters
    """
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return {
        "bmi": round(bmi, 2),
        "category": category,
        "weight_kg": weight_kg,
        "height_m": height_m
    }

@mcp_server.add({
    "Title": "Word Count",
    "Description": "Count words, characters, and lines in text"
})
def word_count(text: str) -> dict:
    """Analyze text statistics.
    
    text: Text to analyze
    """
    lines = text.split('\n')
    words = text.split()
    chars = len(text)
    chars_no_spaces = len(text.replace(' ', ''))
    
    return {
        "lines": len(lines),
        "words": len(words),
        "characters": chars,
        "characters_no_spaces": chars_no_spaces
    }

@app.post("/mcp")
async def handle_mcp(request: MCPRequest):
    """Handle MCP JSON-RPC requests."""
    try:
        # Convert Pydantic model to dict for mcp_server
        request_dict = request.dict()
        response = mcp_server.run(request_dict)
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
async def list_tools():
    """List available MCP tools."""
    return {
        "server": "FastAPI MCP Server",
        "tools": mcp_server.list_tools(),
        "count": len(mcp_server.list_tools())
    }

@app.get("/")
async def root():
    """API information."""
    return {
        "message": "FastAPI MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "mcp": "POST /mcp - Send MCP requests",
            "tools": "GET /tools - List available tools",
            "docs": "GET /docs - API documentation"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI MCP Server...")
    print(f"Available tools: {mcp_server.list_tools()}")
    uvicorn.run(app, host="0.0.0.0", port=8001)