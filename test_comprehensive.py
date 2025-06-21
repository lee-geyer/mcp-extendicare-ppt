import asyncio
import json

async def test_comprehensive():
    """Comprehensive test of all MCP server functionality"""
    from mcp_server import ExtendicarePPTServer, Config
    
    config = Config(
        template_path="../ExtendicareTemplate.pptx",
        output_dir="."
    )
    
    server = ExtendicarePPTServer(config)
    
    print("🚀 Testing MCP Extendicare PowerPoint Server")
    print("=" * 60)
    
    # Test 1: Query all layouts
    print("\n1. Testing query_layouts (all layouts)...")
    all_layouts = await server.query_layouts()
    print(f"   ✅ Found {len(all_layouts)} total layouts")
    
    # Test 2: Query specific features
    print("\n2. Testing query_layouts with features...")
    
    features_to_test = [
        ["chart"],
        ["picture"],
        ["2 column"],
        ["table"],
        ["title"]
    ]
    
    for features in features_to_test:
        layouts = await server.query_layouts(features)
        print(f"   📊 '{features[0]}' layouts: {len(layouts)} found")
        if layouts:
            print(f"      Example: {layouts[0]['name']}")
    
    # Test 3: Get layout details
    print("\n3. Testing get_layout_details...")
    layout_5 = await server.get_layout_details(5)
    print(f"   ✅ Layout 5: {layout_5['name']}")
    print(f"      Placeholders: {len(layout_5['placeholders'])}")
    
    # Test 4: Create presentation with structured format
    print("\n4. Testing create_presentation (structured format)...")
    spec_structured = {
        "slides": [
            {
                "layout_index": 0,
                "content": {
                    "title": "Q4 2024 Results",
                    "subtitle": "Extendicare Financial Performance",
                    "date": "March 21, 2025"
                }
            },
            {
                "layout_index": 7,
                "content": {
                    "title": "Key Financial Metrics",
                    "subtitle": "Year-over-Year Performance",
                    "bullets": [
                        "Revenue increased 12% to $1.2B",
                        "EBITDA margin improved to 18.5%",
                        "Operating expenses reduced by 6%",
                        "Strong cash flow generation"
                    ]
                }
            },
            {
                "layout_index": 17,
                "content": {
                    "title": "Revenue Growth Trends",
                    "subtitle": "Quarterly Performance",
                    "image": "Chart showing quarterly revenue progression"
                }
            }
        ]
    }
    
    output1 = await server.create_presentation(spec_structured)
    print(f"   ✅ Created structured presentation: {output1}")
    
    # Test 5: Create presentation with markdown format
    print("\n5. Testing create_presentation (markdown format)...")
    spec_markdown = {
        "markdown": """
# Strategic Update
## Q4 2024 Highlights

- Exceeded revenue targets by 8%
- Successful acquisition integration
- Enhanced operational efficiency

## Key Achievements

- Market share expansion in core regions
- Technology platform modernization
- Improved resident satisfaction scores
- Cost optimization initiatives delivered savings

## Looking Forward

- Continue strategic growth initiatives
- Focus on operational excellence
- Investment in digital transformation
"""
    }
    
    output2 = await server.create_presentation(spec_markdown)
    print(f"   ✅ Created markdown presentation: {output2}")
    
    # Test 6: Create presentation with natural language
    print("\n6. Testing create_presentation (natural language)...")
    spec_natural = {
        "description": "Create a presentation about Extendicare's digital transformation initiatives, including new technology implementations, staff training programs, and improved resident care outcomes."
    }
    
    output3 = await server.create_presentation(spec_natural)
    print(f"   ✅ Created natural language presentation: {output3}")
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed successfully!")
    print("\nGenerated presentations:")
    print(f"   📄 {output1}")
    print(f"   📄 {output2}")
    print(f"   📄 {output3}")
    
    print("\n💡 The MCP server is ready for Claude Desktop integration!")

if __name__ == "__main__":
    asyncio.run(test_comprehensive())