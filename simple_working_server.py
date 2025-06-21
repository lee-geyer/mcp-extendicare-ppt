#!/usr/bin/env python3
"""
Simple working MCP server for Claude Desktop
"""
import asyncio
import json
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

# Debug output to see if server is starting
print("🚀 Extendicare MCP Server starting...", file=sys.stderr)

# Initialize server
server = Server("extendicare-ppt")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="query_layouts",
            description="Search PowerPoint layouts for Extendicare presentations",
            inputSchema={
                "type": "object",
                "properties": {
                    "features": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Layout features to search for (chart, picture, column, table)"
                    }
                }
            }
        ),
        Tool(
            name="create_presentation",
            description="Create Extendicare-branded PowerPoint presentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Presentation title"
                    },
                    "content": {
                        "type": "string",
                        "description": "Presentation content or description"
                    }
                },
                "required": ["title"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments):
    try:
        if name == "query_layouts":
            # Load layouts data
            with open("template_analysis.json", "r") as f:
                layouts = json.load(f)
            
            features = arguments.get("features", [])
            if not features:
                return {"layouts_found": len(layouts), "message": "All 22 Extendicare layouts available"}
            
            # Filter layouts by features
            matching = []
            for layout in layouts:
                layout_name = layout['name'].lower()
                layout_types = [p['type'].lower() for p in layout['placeholders']]
                
                for feature in features:
                    feature_lower = feature.lower()
                    if (feature_lower in layout_name or 
                        any(feature_lower in ptype for ptype in layout_types)):
                        matching.append({
                            "index": layout['index'],
                            "name": layout['name'],
                            "placeholders": len(layout['placeholders'])
                        })
                        break
            
            return {
                "layouts_found": len(matching),
                "matching_layouts": matching,
                "total_layouts": len(layouts)
            }
        
        elif name == "create_presentation":
            title = arguments.get("title", "Untitled Presentation")
            content = arguments.get("content", "")
            
            # Simple response for now
            return {
                "success": True,
                "message": f"Would create Extendicare presentation: '{title}'",
                "note": "Full implementation creates actual .pptx files using branded template"
            }
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return {"error": str(e)}

async def main():
    print("🔧 Setting up stdio server...", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        print("✅ Server connected and running!", file=sys.stderr)
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    print("🎯 Starting main function...", file=sys.stderr)
    asyncio.run(main())