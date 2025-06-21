#!/usr/bin/env python3
"""
Enhanced MCP Server with AI-Friendly Template Support
Uses semantic layout selection and intelligent content placement
"""
import asyncio
import json
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool
from smart_layout_selector import SmartLayoutSelector

server = Server("extendicare-ppt-v2")

# Initialize the smart selector
try:
    smart_selector = SmartLayoutSelector()
    print("🧠 Smart Layout Selector initialized", file=sys.stderr)
except Exception as e:
    print(f"⚠️ Could not load smart selector: {e}", file=sys.stderr)
    smart_selector = None

@server.list_tools()
async def list_tools():
    """List available tools with enhanced AI capabilities"""
    tools = [
        Tool(
            name="query_layouts",
            description="Search PowerPoint layouts with semantic understanding",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature": {
                        "type": "string",
                        "description": "Layout feature or content type to search for"
                    },
                    "semantic": {
                        "type": "boolean",
                        "description": "Use semantic search with AI-friendly names (default: true)",
                        "default": True
                    }
                }
            }
        ),
        Tool(
            name="recommend_layout",
            description="Get intelligent layout recommendations based on content",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "object",
                        "description": "Content to analyze for layout recommendation"
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of recommendations to return (default: 3)",
                        "default": 3
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="analyze_content",
            description="Analyze content characteristics for presentation planning",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "object",
                        "description": "Content to analyze"
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="get_layout_details",
            description="Get detailed semantic information about a specific layout",
            inputSchema={
                "type": "object",
                "properties": {
                    "layout_id": {
                        "type": "string",
                        "description": "Layout ID or semantic name"
                    }
                },
                "required": ["layout_id"]
            }
        ),
        Tool(
            name="create_presentation",
            description="Create AI-optimized Extendicare presentation with intelligent layout selection",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Presentation title"
                    },
                    "content": {
                        "type": "object",
                        "description": "Presentation content with semantic structure"
                    },
                    "auto_layout": {
                        "type": "boolean",
                        "description": "Use AI to automatically select optimal layouts (default: true)",
                        "default": True
                    }
                },
                "required": ["title", "content"]
            }
        )
    ]
    
    return tools

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls with enhanced AI capabilities"""
    
    if name == "query_layouts":
        return await handle_query_layouts(arguments)
    elif name == "recommend_layout":
        return await handle_recommend_layout(arguments)
    elif name == "analyze_content":
        return await handle_analyze_content(arguments)
    elif name == "get_layout_details":
        return await handle_get_layout_details(arguments)
    elif name == "create_presentation":
        return await handle_create_presentation(arguments)
    else:
        return [{"type": "text", "text": f"Unknown tool: {name}"}]

async def handle_query_layouts(arguments: dict):
    """Enhanced layout querying with semantic search"""
    feature = arguments.get("feature", "all")
    use_semantic = arguments.get("semantic", True)
    
    try:
        # Load layout data
        template_analysis_path = "/Users/leegeyer/Library/CloudStorage/OneDrive-Extendicare(Canada)Inc/Investor Quarterly Reporting/mcp-extendicare-ppt/template_analysis.json"
        with open(template_analysis_path, "r") as f:
            layouts = json.load(f)
        
        if use_semantic and smart_selector:
            # Use semantic metadata if available
            semantic_layouts = smart_selector.metadata.get('layouts', {})
            
            response_text = f"**🧠 AI-Enhanced Layout Search - {feature}**\n\n"
            
            if feature == "all":
                response_text += f"Found {len(semantic_layouts)} AI-optimized layouts:\n\n"
                for layout_id, layout_info in semantic_layouts.items():
                    semantic_name = layout_info.get('semantic_name', f'Layout {layout_id}')
                    purpose = layout_info.get('purpose', 'No description')
                    category = layout_info.get('category', 'unknown')
                    use_cases = layout_info.get('use_cases', [])
                    
                    response_text += f"• **{semantic_name}** (Layout {layout_id})\n"
                    response_text += f"  Purpose: {purpose}\n"
                    response_text += f"  Category: {category}\n"
                    response_text += f"  Best for: {', '.join(use_cases)}\n\n"
            else:
                # Search semantically
                matching_layouts = []
                search_term = feature.lower()
                
                for layout_id, layout_info in semantic_layouts.items():
                    semantic_name = layout_info.get('semantic_name', '').lower()
                    purpose = layout_info.get('purpose', '').lower()
                    category = layout_info.get('category', '').lower()
                    subcategory = layout_info.get('subcategory', '').lower()
                    use_cases = ' '.join(layout_info.get('use_cases', [])).lower()
                    
                    if (search_term in semantic_name or 
                        search_term in purpose or 
                        search_term in category or
                        search_term in subcategory or
                        search_term in use_cases):
                        matching_layouts.append((layout_id, layout_info))
                
                response_text += f"Found {len(matching_layouts)} layouts matching '{feature}':\n\n"
                
                for layout_id, layout_info in matching_layouts:
                    semantic_name = layout_info.get('semantic_name', f'Layout {layout_id}')
                    purpose = layout_info.get('purpose', 'No description')
                    placeholders = layout_info.get('placeholders', {})
                    
                    response_text += f"• **{semantic_name}** (Layout {layout_id})\n"
                    response_text += f"  Purpose: {purpose}\n"
                    response_text += f"  Placeholders ({len(placeholders)}):\n"
                    
                    for placeholder_name, placeholder_info in placeholders.items():
                        semantic_name_ph = placeholder_info.get('semantic_name', placeholder_name)
                        ptype = placeholder_info.get('type', 'unknown')
                        guidelines = placeholder_info.get('content_guidelines', '')
                        
                        response_text += f"    - {semantic_name_ph} ({ptype})\n"
                        if guidelines:
                            response_text += f"      Guide: {guidelines}\n"
                    
                    response_text += "\n"
        else:
            # Fallback to traditional search
            if feature != "all":
                matching_layouts = []
                for layout in layouts:
                    layout_name = layout['name'].lower()
                    if feature.lower() in layout_name or any(feature.lower() in p['type'].lower() for p in layout['placeholders']):
                        matching_layouts.append(layout)
                
                response_text = f"**Extendicare PowerPoint Layouts - {feature}**\n\nFound {len(matching_layouts)} layouts matching '{feature}':\n\n"
                for layout in matching_layouts:
                    response_text += f"• **{layout['name']}** (Layout {layout['index']}) - {len(layout['placeholders'])} placeholders\n"
                    for ph in layout['placeholders']:
                        if ph['type'] not in ['SLIDE_NUMBER (13)', 'FOOTER (15)']:
                            response_text += f"  - {ph['name']}: {ph['type']}\n"
                    response_text += "\n"
            else:
                response_text = f"**Extendicare PowerPoint Templates**\n\nFound {len(layouts)} layouts available. Use semantic search for better results!"
        
        return [{"type": "text", "text": response_text}]
        
    except FileNotFoundError:
        return [{"type": "text", "text": "**Extendicare PowerPoint Server Connected!**\n\nTemplate analysis not available, but server is working."}]

async def handle_recommend_layout(arguments: dict):
    """Intelligent layout recommendation based on content analysis"""
    content = arguments.get("content", {})
    top_n = arguments.get("top_n", 3)
    
    if not smart_selector:
        return [{"type": "text", "text": "**Smart Layout Recommendations Not Available**\n\nSemantic analysis requires AI-friendly metadata."}]
    
    try:
        # Get recommendations
        recommendations = smart_selector.recommend_layouts(content, top_n)
        
        # Analyze the content
        analysis = smart_selector.analyze_content(content)
        
        response_text = f"**🎯 Smart Layout Recommendations**\n\n"
        response_text += f"**Content Analysis:**\n"
        response_text += f"• Type: {analysis.content_type}\n"
        response_text += f"• Structure: {analysis.structure}\n"
        response_text += f"• Text Density: {analysis.text_density}\n"
        response_text += f"• Has Charts: {'Yes' if analysis.has_charts else 'No'}\n"
        response_text += f"• Data Points: {analysis.data_points}\n\n"
        
        response_text += f"**Top {len(recommendations)} Recommendations:**\n\n"
        
        for i, (layout_id, score, reason) in enumerate(recommendations, 1):
            layout_info = smart_selector.layouts.get(layout_id, {})
            semantic_name = layout_info.get('semantic_name', f'Layout {layout_id}')
            purpose = layout_info.get('purpose', 'No description available')
            
            response_text += f"**{i}. {semantic_name}** (Score: {score:.1f})\n"
            response_text += f"   Layout ID: {layout_id}\n"
            response_text += f"   Purpose: {purpose}\n"
            response_text += f"   Why: {reason}\n\n"
        
        return [{"type": "text", "text": response_text}]
        
    except Exception as e:
        return [{"type": "text", "text": f"**Error in Layout Recommendation**\n\nError: {str(e)}"}]

async def handle_analyze_content(arguments: dict):
    """Analyze content characteristics"""
    content = arguments.get("content", {})
    
    if not smart_selector:
        return [{"type": "text", "text": "**Content Analysis Not Available**\n\nRequires AI-friendly metadata."}]
    
    try:
        analysis = smart_selector.analyze_content(content)
        
        response_text = f"**📊 Content Analysis Report**\n\n"
        response_text += f"**Content Characteristics:**\n"
        response_text += f"• Content Type: {analysis.content_type}\n"
        response_text += f"• Structure: {analysis.structure}\n"
        response_text += f"• Text Density: {analysis.text_density}\n"
        response_text += f"• Contains Charts: {'Yes' if analysis.has_charts else 'No'}\n"
        response_text += f"• Contains Tables: {'Yes' if analysis.has_tables else 'No'}\n"
        response_text += f"• Contains Images: {'Yes' if analysis.has_images else 'No'}\n"
        response_text += f"• Data Points Found: {analysis.data_points}\n"
        
        if analysis.key_metrics:
            response_text += f"• Key Metrics: {', '.join(analysis.key_metrics)}\n"
        
        response_text += f"\n**Presentation Recommendations:**\n"
        
        if analysis.content_type == "data_visualization":
            response_text += "• Use chart-focused layouts\n"
            response_text += "• Include data analysis placeholders\n"
            response_text += "• Consider dashboard layouts for multiple metrics\n"
        elif analysis.content_type == "narrative":
            response_text += "• Use text-heavy layouts\n"
            response_text += "• Consider single-column layouts for readability\n"
            response_text += "• Break long content into multiple slides\n"
        elif analysis.structure == "comparison":
            response_text += "• Use two-column comparison layouts\n"
            response_text += "• Ensure balanced content placement\n"
            response_text += "• Consider before/after visualization\n"
        
        return [{"type": "text", "text": response_text}]
        
    except Exception as e:
        return [{"type": "text", "text": f"**Error in Content Analysis**\n\nError: {str(e)}"}]

async def handle_get_layout_details(arguments: dict):
    """Get detailed information about a specific layout"""
    layout_id = arguments.get("layout_id", "")
    
    if not smart_selector:
        return [{"type": "text", "text": "**Layout Details Not Available**\n\nRequires AI-friendly metadata."}]
    
    try:
        layout_details = smart_selector.get_layout_details(layout_id)
        
        if "error" in layout_details:
            return [{"type": "text", "text": f"**Error:** {layout_details['error']}"}]
        
        semantic_name = layout_details.get('semantic_name', f'Layout {layout_id}')
        purpose = layout_details.get('purpose', 'No description')
        category = layout_details.get('category', 'unknown')
        structure = layout_details.get('structure', 'unknown')
        use_cases = layout_details.get('use_cases', [])
        placeholders = layout_details.get('placeholders', {})
        summary = layout_details.get('placeholder_summary', {})
        
        response_text = f"**📋 Layout Details: {semantic_name}**\n\n"
        response_text += f"**Overview:**\n"
        response_text += f"• Layout ID: {layout_id}\n"
        response_text += f"• Purpose: {purpose}\n"
        response_text += f"• Category: {category}\n"
        response_text += f"• Structure: {structure}\n"
        response_text += f"• Best Used For: {', '.join(use_cases)}\n\n"
        
        response_text += f"**Placeholder Summary:**\n"
        response_text += f"• Total Placeholders: {summary.get('total_count', 0)}\n"
        response_text += f"• Required Placeholders: {summary.get('required_count', 0)}\n"
        
        by_type = summary.get('by_type', {})
        if by_type:
            response_text += f"• By Type: {', '.join(f'{count} {ptype}' for ptype, count in by_type.items())}\n"
        
        by_column = summary.get('by_column', {})
        if any(col != 'none' for col in by_column.keys()):
            response_text += f"• By Column: {', '.join(f'{count} {col}' for col, count in by_column.items() if col != 'none')}\n"
        
        response_text += f"\n**Detailed Placeholders:**\n"
        
        for placeholder_name, placeholder_info in placeholders.items():
            semantic_name_ph = placeholder_info.get('semantic_name', placeholder_name)
            ptype = placeholder_info.get('type', 'unknown')
            idx = placeholder_info.get('idx', 'unknown')
            ppt_type = placeholder_info.get('ppt_type', 'unknown')
            guidelines = placeholder_info.get('content_guidelines', '')
            required = placeholder_info.get('required', False)
            column = placeholder_info.get('column', '')
            
            response_text += f"\n**{semantic_name_ph}**\n"
            response_text += f"  • Type: {ptype}\n"
            response_text += f"  • PowerPoint Type: {ppt_type}\n"
            response_text += f"  • Index: {idx}\n"
            response_text += f"  • Required: {'Yes' if required else 'No'}\n"
            if column:
                response_text += f"  • Column: {column}\n"
            if guidelines:
                response_text += f"  • Guidelines: {guidelines}\n"
        
        return [{"type": "text", "text": response_text}]
        
    except Exception as e:
        return [{"type": "text", "text": f"**Error Getting Layout Details**\n\nError: {str(e)}"}]

async def handle_create_presentation(arguments: dict):
    """Create presentation with AI-optimized layout selection"""
    title = arguments.get("title", "Untitled Presentation")
    content = arguments.get("content", {})
    auto_layout = arguments.get("auto_layout", True)
    
    response_text = f"**🚀 AI-Enhanced Presentation Creation**\n\n"
    response_text += f"**Title:** {title}\n"
    response_text += f"**Auto Layout:** {'Enabled' if auto_layout else 'Disabled'}\n\n"
    
    if auto_layout and smart_selector:
        try:
            # Analyze content and recommend layouts
            analysis = smart_selector.analyze_content(content)
            recommendations = smart_selector.recommend_layouts(content, top_n=1)
            
            response_text += f"**AI Analysis:**\n"
            response_text += f"• Content Type: {analysis.content_type}\n"
            response_text += f"• Recommended Layout: {smart_selector.layouts[recommendations[0][0]].get('semantic_name', 'Unknown')}\n"
            response_text += f"• Confidence: {recommendations[0][1]:.1f}/5.0\n\n"
        except Exception as e:
            response_text += f"**AI Analysis Failed:** {str(e)}\n\n"
    
    response_text += f"**Implementation Notes:**\n"
    response_text += f"• Full presentation generation would create .pptx file\n"
    response_text += f"• Would use Extendicare branded template\n"
    response_text += f"• AI would optimize placeholder content placement\n"
    response_text += f"• Semantic naming enables intelligent content mapping\n"
    
    return [{"type": "text", "text": response_text}]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())