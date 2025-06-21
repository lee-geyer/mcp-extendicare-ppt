#!/usr/bin/env python3
"""
Simple test MCP server to verify connection
"""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

# Create a simple server
server = Server("test-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="test_tool",
            description="A simple test tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "A test message"
                    }
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments):
    if name == "test_tool":
        message = arguments.get("message", "Hello from Extendicare MCP!")
        return {"response": f"Test successful: {message}"}
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())