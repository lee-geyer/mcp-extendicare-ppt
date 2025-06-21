import asyncio
import json

async def test_server():
    # Test imports and basic functionality
    from mcp_server import ExtendicarePPTServer, Config
    
    config = Config(
        template_path="../ExtendicareTemplate.pptx",
        output_dir="."
    )
    
    server = ExtendicarePPTServer(config)
    
    # Test query layouts
    print("Testing query_layouts...")
    layouts = await server.query_layouts(["chart"])
    print(f"Found {len(layouts)} layouts with charts")
    
    # Test create presentation
    print("\nTesting create_presentation...")
    spec = {
        "slides": [
            {
                "layout_index": 0,
                "content": {
                    "title": "Test Presentation",
                    "subtitle": "MCP Server Test",
                    "date": "Today"
                }
            }
        ]
    }
    
    output_path = await server.create_presentation(spec)
    print(f"Created presentation: {output_path}")

if __name__ == "__main__":
    asyncio.run(test_server())