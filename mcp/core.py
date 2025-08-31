import inspect
import json
import logging
import time
from functools import wraps

class MCP:
    """
    Message Control Protocol (MCP) base class.
    Handles the registration and execution of tools.
    """
    
    # A simple class to use as a type hint for required parameters
    class required:
        pass
    
    def __init__(self, name="MCP Server", version="1.0.0", log_level=logging.INFO, enable_logging=True):
        # A dictionary to store registered tools, using the function name as the key.
        self.tools = {}
        self.initialized = False
        self.server_name = name
        self.server_version = version
        self.enable_logging = enable_logging
        
        # Set up logging
        self.logger = logging.getLogger(f"MCP.{name.replace(' ', '_')}")
        
        if enable_logging:
            self.logger.setLevel(log_level)
            
            # Create console handler if no handlers exist
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        else:
            # Disable logging by setting level to CRITICAL+1
            self.logger.setLevel(logging.CRITICAL + 1)
            # Add null handler to prevent any output
            if not self.logger.handlers:
                self.logger.addHandler(logging.NullHandler())

    def register_tool(self, tool_name, tool_info):
        """Register a tool with the MCP."""
        self.tools[tool_name] = tool_info
        self._log('info', f"Registered tool: {tool_name} - {tool_info.get('description', 'No description')}")

    def list_tools(self):
        """List the names of all registered tools."""
        return list(self.tools.keys())
    
    def set_log_level(self, level):
        """Set the logging level for this MCP instance."""
        if self.enable_logging:
            self.logger.setLevel(level)
            self.logger.info(f"Log level changed to: {logging.getLevelName(level) if hasattr(logging, 'getLevelName') else str(level)}")
    
    def enable_logs(self, enable=True, log_level=logging.INFO):
        """Enable or disable logging for this MCP instance."""
        self.enable_logging = enable
        if enable:
            self.logger.setLevel(log_level)
            if not any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
            self.logger.info(f"Logging enabled for {self.server_name}")
        else:
            self.logger.setLevel(logging.CRITICAL + 1)
            # Remove stream handlers and add null handler
            self.logger.handlers = [h for h in self.logger.handlers if not isinstance(h, logging.StreamHandler)]
            if not self.logger.handlers:
                self.logger.addHandler(logging.NullHandler())

    def _log(self, level, message, *args):
        """Log a message only if logging is enabled."""
        if self.enable_logging:
            getattr(self.logger, level)(message, *args)

    def _infer_param_type_from_annotation(self, annotation):
        """Infer JSON Schema type from Python type annotation."""
        if annotation == inspect.Parameter.empty or annotation is None:
            return "string"  # Default to string
        
        # Handle common types
        type_mapping = {
            str: "string",
            int: "integer", 
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object"
        }
        
        # Check if annotation is a type
        if annotation in type_mapping:
            return type_mapping[annotation]
        
        # Handle typing module annotations
        if hasattr(annotation, '__origin__'):
            origin = annotation.__origin__
            if origin in type_mapping:
                return type_mapping[origin]
        
        # Handle string annotations (for forward references)
        if isinstance(annotation, str):
            lower_annotation = annotation.lower()
            if 'int' in lower_annotation:
                return "integer"
            elif 'float' in lower_annotation or 'number' in lower_annotation:
                return "number"
            elif 'bool' in lower_annotation:
                return "boolean"
            elif 'list' in lower_annotation or 'array' in lower_annotation:
                return "array"
            elif 'dict' in lower_annotation or 'object' in lower_annotation:
                return "object"
        
        # Default fallback
        return "string"

    def add(self, tool_info_dict):
        """Decorator to register a function as a tool with this MCP instance."""
        def wrapper(func):
            # Use Python's inspect module to get the function signature
            sig = inspect.signature(func)
            required_params = []
            properties = {}
            
            for name, param in sig.parameters.items():
                # Check if parameter is required (no default value)
                is_required = param.default is inspect.Parameter.empty
                if is_required:
                    required_params.append(name)
                
                # Infer parameter type from annotation
                param_type = self._infer_param_type_from_annotation(param.annotation)
                
                # Get parameter description from docstring or use default
                param_description = f"Parameter {name}"
                
                # Try to extract parameter description from function docstring
                if func.__doc__:
                    doc_lines = func.__doc__.strip().split('\n')
                    for line in doc_lines:
                        line = line.strip()
                        if line.startswith(f"{name}:") or line.startswith(f"- {name}:"):
                            param_description = line.split(':', 1)[1].strip()
                            break
                        elif f"param {name}" in line.lower() or f"parameter {name}" in line.lower():
                            # Handle different docstring formats
                            if ':' in line:
                                param_description = line.split(':', 1)[1].strip()
                            break
                
                properties[name] = {
                    "type": param_type,
                    "description": param_description
                }

            tool_info = {
                "title": tool_info_dict.get('Title'),
                "description": tool_info_dict.get('Description'),
                "function": func,
                "required_params": required_params,
                "properties": properties
            }
            # Register the tool with this MCP instance
            self.register_tool(func.__name__, tool_info)

            # Preserve the original function's metadata
            @wraps(func)
            def inner_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return inner_wrapper
        return wrapper

    def initialize(self, params=None):
        """
        Handle MCP initialize request.
        Returns connection capabilities and marks the session as initialized.
        """
        self._log('info', f"Initializing MCP server '{self.server_name}' v{self.server_version}")
        if params:
            self._log('debug', f"Initialize params: {json.dumps(params)}")
        
        self.initialized = True
        
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": False
                }
            },
            "serverInfo": {
                "name": self.server_name,
                "version": self.server_version
            }
        }
        
        self._log('info', f"MCP server initialized successfully. Available tools: {len(self.tools)}")
        return result

    def run(self, request_json):
        """
        Run the appropriate tool based on JSON-RPC 2.0 request.
        Handles both MCP initialization and tool execution.
        Request format:
        {
            "jsonrpc": "2.0",
            "method": "tool_name",
            "params": {...},
            "id": "request_id"
        }
        """
        start_time = time.time()
        request_id = None
        method = None
        
        try:
            # Log incoming request
            if isinstance(request_json, str):
                self.logger.debug(f"Incoming request: {request_json}")
                request = json.loads(request_json)
            else:
                self.logger.debug(f"Incoming request: {json.dumps(request_json)}")
                request = request_json
            
            # Validate JSON-RPC 2.0 format
            if request.get('jsonrpc') != '2.0':
                error_response = self._error_response(None, -32600, "Invalid Request", "Missing or invalid jsonrpc version")
                self.logger.warning(f"Invalid JSON-RPC version in request")
                return error_response
            
            request_id = request.get('id')
            method = request.get('method')
            params = request.get('params', {})

            self.logger.info(f"Processing request - Method: {method}, ID: {request_id}")

            if not method:
                error_response = self._error_response(request_id, -32600, "Invalid Request", "Missing method")
                self.logger.error(f"Missing method in request ID: {request_id}")
                return error_response

            # Handle MCP protocol methods
            if method == "initialize":
                result = self.initialize(params)
                response = self._success_response(request_id, result)
                execution_time = (time.time() - start_time) * 1000
                self.logger.info(f"Initialize completed - ID: {request_id}, Time: {execution_time:.2f}ms")
                return response
            
            if method == "initialized" or method == "notifications/initialized":
                # Client confirmation of initialization - just return success
                response = self._success_response(request_id, {})
                self.logger.info(f"Initialization confirmed - ID: {request_id}")
                return response
            
            if method == "tools/list":
                # Return list of available tools
                tools_list = []
                for tool_name, tool_info in self.tools.items():
                    tool_schema = {
                        "name": tool_name,
                        "description": tool_info.get('description', ''),
                        "inputSchema": {
                            "type": "object",
                            "properties": tool_info.get('properties', {}),
                            "required": tool_info.get('required_params', [])
                        }
                    }
                    tools_list.append(tool_schema)
                
                response = self._success_response(request_id, {"tools": tools_list})
                execution_time = (time.time() - start_time) * 1000
                self.logger.info(f"Tools list completed - ID: {request_id}, Count: {len(tools_list)}, Time: {execution_time:.2f}ms")
                return response
            
            if method == "tools/call":
                # Handle tool execution via tools/call method
                tool_name = params.get('name')
                tool_arguments = params.get('arguments', {})
                
                if not tool_name:
                    error_response = self._error_response(request_id, -32602, "Invalid params", "Missing tool name in tools/call")
                    self.logger.error(f"Missing tool name in tools/call - ID: {request_id}")
                    return error_response
                
                tool_info = self.tools.get(tool_name)
                if not tool_info:
                    error_response = self._error_response(request_id, -32601, "Method not found", f"Tool '{tool_name}' not found")
                    self.logger.error(f"Tool not found in tools/call: {tool_name} - ID: {request_id}")
                    return error_response

                self.logger.info(f"Executing tool via tools/call: {tool_name} with arguments: {json.dumps(tool_arguments)} - ID: {request_id}")

                tool_func = tool_info['function']
                # Simple validation for required parameters
                required_params = tool_info['required_params']
                missing_params = [p for p in required_params if p not in tool_arguments]
                if missing_params:
                    error_response = self._error_response(
                        request_id, 
                        -32602, 
                        "Invalid params", 
                        f"Missing required parameters: {', '.join(missing_params)}"
                    )
                    self.logger.error(f"Missing parameters for {tool_name}: {missing_params} - ID: {request_id}")
                    return error_response

                # Execute the tool with the provided parameters
                result = tool_func(**tool_arguments)
                
                # Format response according to MCP tools/call spec
                tool_response = {
                    "content": [
                        {
                            "type": "text",
                            "text": str(result)
                        }
                    ]
                }
                
                response = self._success_response(request_id, tool_response)
                
                execution_time = (time.time() - start_time) * 1000
                self.logger.info(f"Tool execution completed via tools/call - Method: {tool_name}, ID: {request_id}, Time: {execution_time:.2f}ms")
                self.logger.debug(f"Tool result for {tool_name}: {json.dumps(result) if result is not None else 'None'}")
                
                return response

            # For regular tool calls, check if initialized (in production)
            # For simplicity, we'll auto-initialize if not done
            if not self.initialized:
                self.logger.info("Auto-initializing MCP server for tool execution")
                self.initialize()

            # Handle regular tool execution
            tool_info = self.tools.get(method)
            if not tool_info:
                error_response = self._error_response(request_id, -32601, "Method not found", f"Tool '{method}' not found")
                self.logger.error(f"Tool not found: {method} - ID: {request_id}")
                return error_response

            self.logger.info(f"Executing tool: {method} with params: {json.dumps(params)} - ID: {request_id}")

            tool_func = tool_info['function']
            # Simple validation for required parameters
            required_params = tool_info['required_params']
            missing_params = [p for p in required_params if p not in params]
            if missing_params:
                error_response = self._error_response(
                    request_id, 
                    -32602, 
                    "Invalid params", 
                    f"Missing required parameters: {', '.join(missing_params)}"
                )
                self.logger.error(f"Missing parameters for {method}: {missing_params} - ID: {request_id}")
                return error_response

            # Execute the tool with the provided parameters
            result = tool_func(**params)
            response = self._success_response(request_id, result)
            
            execution_time = (time.time() - start_time) * 1000
            self.logger.info(f"Tool execution completed - Method: {method}, ID: {request_id}, Time: {execution_time:.2f}ms")
            self.logger.debug(f"Tool result for {method}: {json.dumps(result) if result is not None else 'None'}")
            
            return response

        except json.JSONDecodeError as e:
            error_response = self._error_response(None, -32700, "Parse error", "Invalid JSON")
            self.logger.error(f"JSON parse error: {str(e)}")
            return error_response
        except Exception as e:
            # Catch all exceptions during execution for robust error handling
            error_response = self._error_response(
                request_id,
                -32603,
                "Internal error", 
                f"An error occurred during tool execution: {str(e)}"
            )
            execution_time = (time.time() - start_time) * 1000
            self.logger.error(f"Internal error - Method: {method}, ID: {request_id}, Time: {execution_time:.2f}ms, Error: {str(e)}")
            return error_response
    
    def _success_response(self, request_id, result):
        """Create a JSON-RPC 2.0 success response."""
        response = {
            "jsonrpc": "2.0",
            "result": result
        }
        if request_id is not None:
            response["id"] = request_id
        return response
    
    def _error_response(self, request_id, code, message, data=None):
        """Create a JSON-RPC 2.0 error response."""
        error = {
            "code": code,
            "message": message
        }
        if data:
            error["data"] = data
            
        response = {
            "jsonrpc": "2.0",
            "error": error
        }
        if request_id is not None:
            response["id"] = request_id
        return response