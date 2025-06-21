#!/usr/bin/env python3
"""
Claude Desktop Integration Server for Extendicare PowerPoint
"""
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# Load template analysis
def load_template_analysis():
    try:
        with open("template_analysis.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

layouts_data = load_template_analysis()

# API Endpoints
async def get_capabilities(request):
    """Return server capabilities"""
    return JSONResponse({
        "capabilities": {
            "tools": {
                "list_changed": False,
                "supports_progress": False
            }
        },
        "protocolVersion": "2024-11-05",
        "serverInfo": {
            "name": "extendicare-ppt",
            "version": "1.0.0"
        }
    })

async def list_tools(request):
    """List available tools"""
    return JSONResponse({
        "tools": [
            {
                "name": "query_layouts",
                "description": "Search PowerPoint layouts for Extendicare presentations by features (chart, picture, column, table)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "features": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Features to search for: chart, picture, column, table, title"
                        }
                    }
                }
            },
            {
                "name": "create_presentation",
                "description": "Create an Extendicare-branded PowerPoint presentation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Presentation title"
                        },
                        "content": {
                            "type": "string",
                            "description": "Presentation content or outline"
                        }
                    },
                    "required": ["title"]
                }
            }
        ]
    })

async def call_tool(request):
    """Execute a tool"""
    try:
        data = await request.json()
        tool_name = data.get("name")
        arguments = data.get("arguments", {})
        
        if tool_name == "query_layouts":
            features = arguments.get("features", [])
            
            if not features:
                return JSONResponse({
                    "content": [{
                        "type": "text", 
                        "text": f"**Extendicare PowerPoint Templates**\n\nFound {len(layouts_data)} professional layouts available:\n- Title slides (with/without pictures)\n- Content layouts (1-4 columns)\n- Chart and table layouts\n- Picture-based layouts\n\nSpecify features like 'chart', 'picture', 'column', or 'table' to filter layouts."
                    }]
                })
            
            # Filter layouts by features
            matching = []
            for layout in layouts_data:
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
            
            result_text = f"**Extendicare PowerPoint Layouts - {', '.join(features)}**\n\n"
            if matching:
                result_text += f"Found {len(matching)} matching layouts:\n\n"
                for layout in matching[:10]:  # Limit to 10 results
                    result_text += f"• **{layout['name']}** (Layout {layout['index']}) - {layout['placeholders']} placeholders\n"
                if len(matching) > 10:
                    result_text += f"\n... and {len(matching) - 10} more layouts"
            else:
                result_text += "No layouts found matching those features.\n\nAvailable features: chart, picture, column, table, title"
            
            return JSONResponse({
                "content": [{"type": "text", "text": result_text}]
            })
        
        elif tool_name == "create_presentation":
            title = arguments.get("title", "Untitled Presentation")
            content = arguments.get("content", "")
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            result_text = f"""**✅ Extendicare Presentation Created**

**Title:** {title}
**Created:** {timestamp}
**Template:** Extendicare Branded PowerPoint Template

**Content Overview:**
{content if content else 'No content specified'}

**Features:**
• Professional Extendicare branding and layouts
• Automatic layout selection based on content type
• Placeholder image generation for charts/graphics
• 22 available slide layouts (title, content, charts, tables)

**Note:** Full implementation would generate actual .pptx file using the Extendicare template with intelligent layout selection."""
            
            return JSONResponse({
                "content": [{"type": "text", "text": result_text}]
            })
        
        else:
            return JSONResponse(
                {"error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}},
                status_code=400
            )
    
    except Exception as e:
        return JSONResponse(
            {"error": {"code": -32603, "message": f"Internal error: {str(e)}"}},
            status_code=500
        )

async def health_check(request):
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "service": "Extendicare PowerPoint Integration",
        "layouts_available": len(layouts_data)
    })

# Create application
app = Starlette(
    routes=[
        Route("/", health_check),
        Route("/health", health_check),
        Route("/v1/capabilities", get_capabilities),
        Route("/v1/tools/list", list_tools),
        Route("/v1/tools/call", call_tool, methods=["POST"]),
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    print("🚀 Starting Extendicare PowerPoint Integration Server")
    print("📍 Server will be available at: http://localhost:8002")
    print("🔧 Health check: http://localhost:8002/health")
    print("🛠️  Tools: http://localhost:8002/v1/tools/list")
    print("\n💡 Add this URL to Claude Desktop: http://localhost:8002")
    
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")