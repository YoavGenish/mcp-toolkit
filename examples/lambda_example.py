"""
AWS Lambda example showing how to integrate mcp-lite with serverless functions.
Deploy using AWS SAM, Serverless Framework, or AWS CDK.
"""

import json
import logging
from mcp import MCP

# Configure logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create MCP server instance
mcp_server = MCP("Lambda MCP Server", "1.0.0", enable_logging=False)

@mcp_server.add({
    "Title": "Process Text",
    "Description": "Process text with various transformations"
})
def process_text(text: str, operation: str = "upper") -> dict:
    """Process text with different operations.
    
    text: Text to process
    operation: Operation to perform (upper, lower, reverse, length)
    """
    operations = {
        "upper": text.upper(),
        "lower": text.lower(),
        "reverse": text[::-1],
        "length": str(len(text))
    }
    
    result = operations.get(operation, text)
    
    return {
        "original": text,
        "operation": operation,
        "result": result,
        "processed_at": "lambda"
    }

@mcp_server.add({
    "Title": "Generate UUID",
    "Description": "Generate a UUID"
})
def generate_uuid() -> str:
    """Generate a UUID."""
    import uuid
    return str(uuid.uuid4())

@mcp_server.add({
    "Title": "Environment Info",
    "Description": "Get Lambda environment information"
})
def environment_info() -> dict:
    """Get environment information."""
    import os
    return {
        "aws_region": os.environ.get("AWS_REGION", "unknown"),
        "function_name": os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "unknown"),
        "function_version": os.environ.get("AWS_LAMBDA_FUNCTION_VERSION", "unknown"),
        "memory_limit": os.environ.get("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", "unknown"),
        "tools_available": len(mcp_server.list_tools())
    }

def lambda_handler(event, context):
    """
    AWS Lambda handler for MCP requests.
    
    Expected event format (API Gateway):
    {
        "body": "{\"jsonrpc\":\"2.0\",\"method\":\"tool_name\",\"params\":{},\"id\":1}",
        "headers": {...},
        "httpMethod": "POST",
        ...
    }
    """
    
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Handle different event sources
        if 'body' in event:
            # API Gateway format
            body = event['body']
            if isinstance(body, str):
                request_data = json.loads(body)
            else:
                request_data = body
        elif 'Records' in event:
            # SQS/SNS format
            request_data = json.loads(event['Records'][0]['body'])
        else:
            # Direct invocation format
            request_data = event
        
        logger.info(f"Processing MCP request: {json.dumps(request_data)}")
        
        # Process the MCP request
        response = mcp_server.run(request_data)
        
        logger.info(f"MCP response: {json.dumps(response)}")
        
        # Return appropriate format for API Gateway
        if 'body' in event:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps(response)
            }
        else:
            # Direct invocation
            return response
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        error_response = {
            'statusCode': 400,
            'body': json.dumps({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32700,
                    'message': 'Parse error',
                    'data': str(e)
                },
                'id': None
            })
        }
        return error_response
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        error_response = {
            'statusCode': 500,
            'body': json.dumps({
                'jsonrpc': '2.0',
                'error': {
                    'code': -32603,
                    'message': 'Internal error',
                    'data': str(e)
                },
                'id': None
            })
        }
        return error_response

# For local testing
if __name__ == "__main__":
    # Test the Lambda handler locally
    test_event = {
        "body": json.dumps({
            "jsonrpc": "2.0",
            "method": "process_text",
            "params": {"text": "Hello World", "operation": "upper"},
            "id": 1
        })
    }
    
    result = lambda_handler(test_event, None)
    print("Test result:")
    print(json.dumps(result, indent=2))