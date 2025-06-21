#!/usr/bin/env python3
"""
Simple wrapper to run the MCP server without uv
"""
import sys
import os
import subprocess

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set up environment
os.environ['PYTHONPATH'] = project_dir
os.chdir(project_dir)

# Import and run the server
from mcp_server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())