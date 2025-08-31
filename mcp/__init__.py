"""
MCP Lite - Lightweight Model Context Protocol implementation

A decorator-based library for easily creating MCP-compatible tools from Python functions.
Handles the MCP protocol while letting you choose your own transport layer.
"""

from .core import MCP

__version__ = "0.1.0"
__all__ = ["MCP"]