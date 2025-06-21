#!/usr/bin/env python3
"""
Direct test of our MCP server
"""
import asyncio
import json
import sys
from simple_working_server import server

async def test_server():
    print("🧪 Testing MCP Server directly...")
    
    # Test list_tools
    print("\n1. Testing list_tools()...")
    try:
        tools = await server._tool_handlers["list_tools"]()
        print(f"   ✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"      - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test call_tool - query_layouts
    print("\n2. Testing call_tool('query_layouts')...")
    try:
        result = await server._tool_handlers["call_tool"]("query_layouts", {"features": ["chart"]})
        print(f"   ✅ Result: {result}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test call_tool - create_presentation
    print("\n3. Testing call_tool('create_presentation')...")
    try:
        result = await server._tool_handlers["call_tool"]("create_presentation", {
            "title": "Test Presentation",
            "content": "This is a test"
        })
        print(f"   ✅ Result: {result}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🎉 MCP Server test completed!")

if __name__ == "__main__":
    asyncio.run(test_server())