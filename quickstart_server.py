#!/usr/bin/env python3
"""
MCP Server following official quickstart pattern
"""
import asyncio
import json
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

server = Server("extendicare-ppt")

@server.list_tools()
async def list_tools():
    """List available tools"""
    return [
        Tool(
            name="query_layouts",
            description="Query Extendicare PowerPoint layouts",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature": {
                        "type": "string",
                        "description": "Layout feature to search for"
                    }
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls"""
    if name == "query_layouts":
        feature = arguments.get("feature", "all")
        
        # Load layout data
        try:
            template_analysis_path = "/Users/leegeyer/Library/CloudStorage/OneDrive-Extendicare(Canada)Inc/Investor Quarterly Reporting/mcp-extendicare-ppt/template_analysis.json"
            with open(template_analysis_path, "r") as f:
                layouts = json.load(f)
            
            # Filter layouts if feature specified
            if feature != "all":
                matching_layouts = []
                for layout in layouts:
                    layout_name = layout['name'].lower()
                    if feature.lower() in layout_name or any(feature.lower() in p['type'].lower() for p in layout['placeholders']):
                        matching_layouts.append(layout)
                
                response_text = f"**Extendicare PowerPoint Layouts - {feature}**\n\nFound {len(matching_layouts)} layouts matching '{feature}':\n\n"
                for layout in matching_layouts:  # Show all matching layouts
                    response_text += f"• **{layout['name']}** (Layout {layout['index']}) - {len(layout['placeholders'])} placeholders\n"
            else:
                response_text = f"**Extendicare PowerPoint Templates**\n\nFound {len(layouts)} professional layouts available:\n• Title slides (with/without pictures)\n• Content layouts (1-4 columns)\n• Chart and table layouts\n• Picture-based layouts"
                
        except FileNotFoundError:
            response_text = "**Extendicare PowerPoint Server Connected!**\n\nTemplate analysis not available, but server is working.\nThe full server can create branded PowerPoint presentations."
        
        return [{"type": "text", "text": response_text}]
    
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