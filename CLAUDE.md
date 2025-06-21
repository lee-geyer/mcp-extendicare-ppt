# MCP Extendicare PowerPoint Server Development Guide

## Project Overview
Build an MCP (Model Context Protocol) server that enables AI assistants to create PowerPoint presentations using the Extendicare branded template with intelligent layout selection.

## Initial Setup

### 1. Create Project Structure
```bash
# Create project directory
mkdir mcp-extendicare-ppt
cd mcp-extendicare-ppt

# Initialize uv project
uv init

# Add required dependencies
uv add python-pptx pillow mcp pydantic
```

### 2. Create Template Analysis Script
First, let's verify the template analysis with the .pptx version:

```python
# create file: analyze_template.py
from pptx import Presentation
import json
from pathlib import Path

def analyze_template(template_path):
    """Analyze PowerPoint template and extract layout information"""
    
    # Load the template (use .pptx version)
    prs = Presentation(template_path)
    
    # Get basic info
    print(f"Total slide layouts: {len(prs.slide_layouts)}")
    print("=" * 80)
    
    # List all layouts with their names and placeholder info
    layouts_info = []
    
    for idx, layout in enumerate(prs.slide_layouts):
        layout_data = {
            "index": idx,
            "name": layout.name,
            "placeholders": []
        }
        
        for placeholder in layout.placeholders:
            ph_info = {
                "idx": placeholder.placeholder_format.idx,
                "type": str(placeholder.placeholder_format.type),
                "name": placeholder.name,
                "has_text_frame": hasattr(placeholder, 'text_frame')
            }
            layout_data["placeholders"].append(ph_info)
        
        layouts_info.append(layout_data)
        
        # Print layout info
        print(f"\nLayout {idx}: {layout.name}")
        print(f"  Placeholders: {len(layout.placeholders)}")
        for ph in layout_data["placeholders"]:
            print(f"    - idx: {ph['idx']}, name: '{ph['name']}', type: {ph['type']}")
    
    # Save to JSON
    output_file = "template_analysis.json"
    with open(output_file, "w") as f:
        json.dump(layouts_info, f, indent=2)
    
    print(f"\n{'=' * 80}")
    print(f"Analysis saved to {output_file}")
    
    return layouts_info

if __name__ == "__main__":
    # UPDATE THIS PATH to your .pptx template
    template_path = "path/to/your/Extendicare.pptx"
    
    if not Path(template_path).exists():
        print(f"Error: Template file not found at {template_path}")
        print("Please update the template_path variable")
    else:
        analyze_template(template_path)
```

### 3. Create Core MCP Server Structure

```python
# create file: mcp_server.py
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from mcp import Protocol, Server
from mcp.types import (
    GetServerCapabilitiesResult,
    CallToolResult,
    Tool,
    Parameter,
    UNSET
)
from pydantic import BaseModel, Field
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from PIL import Image, ImageDraw, ImageFont
import io

# Configuration
class Config(BaseModel):
    template_path: str = Field(description="Path to Extendicare PowerPoint template")
    output_dir: str = Field(default=".", description="Output directory for generated presentations")

# Load template analysis
def load_template_analysis():
    with open("template_analysis.json", "r") as f:
        return json.load(f)

class ExtendicarePPTServer:
    def __init__(self, config: Config):
        self.config = config
        self.template_path = Path(config.template_path)
        self.output_dir = Path(config.output_dir)
        self.layouts = load_template_analysis()
        
        # Verify template exists
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
    
    def create_placeholder_image(self, description: str, width: int = 800, height: int = 600) -> io.BytesIO:
        """Create a placeholder image with description text"""
        # Create image with light gray background
        img = Image.new('RGB', (width, height), color='#E0E0E0')
        draw = ImageDraw.Draw(img)
        
        # Add border
        border_width = 2
        draw.rectangle(
            [(0, 0), (width-1, height-1)],
            outline='#808080',
            width=border_width
        )
        
        # Add text
        try:
            # Try to use a nice font, fallback to default if not available
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position (centered)
        text_bbox = draw.textbbox((0, 0), description, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text
        draw.text((x, y), description, fill='#404040', font=font)
        
        # Save to BytesIO
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return img_io
    
    async def query_layouts(self, features: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Query layouts by features (e.g., 'chart', 'picture', '2 column')"""
        results = []
        
        for layout in self.layouts:
            if features:
                # Check if layout matches any of the requested features
                layout_name_lower = layout['name'].lower()
                placeholder_types = [p['type'].lower() for p in layout['placeholders']]
                
                matches = False
                for feature in features:
                    feature_lower = feature.lower()
                    if (feature_lower in layout_name_lower or
                        any(feature_lower in ptype for ptype in placeholder_types)):
                        matches = True
                        break
                
                if matches:
                    results.append(layout)
            else:
                results.append(layout)
        
        return results
    
    async def get_layout_details(self, layout_index: int) -> Dict[str, Any]:
        """Get detailed information about a specific layout"""
        if 0 <= layout_index < len(self.layouts):
            return self.layouts[layout_index]
        else:
            raise ValueError(f"Layout index {layout_index} out of range (0-{len(self.layouts)-1})")
    
    async def create_slide(self, layout_index: int, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single slide with specified content"""
        # This will be called by create_presentation
        # Returns slide data for inclusion in presentation
        return {
            "layout_index": layout_index,
            "content": content
        }
    
    async def create_presentation(self, spec: Dict[str, Any]) -> str:
        """Create a complete presentation based on specification"""
        prs = Presentation(str(self.template_path))
        
        # Parse specification - supports multiple input formats
        slides_data = self._parse_presentation_spec(spec)
        
        # Create slides
        for slide_data in slides_data:
            layout_index = slide_data.get('layout_index', 0)
            content = slide_data.get('content', {})
            
            # Get layout
            if layout_index >= len(prs.slide_layouts):
                layout_index = 0  # Fallback to first layout
            
            slide_layout = prs.slide_layouts[layout_index]
            slide = prs.slides.add_slide(slide_layout)
            
            # Fill placeholders
            for placeholder in slide.placeholders:
                ph_name = placeholder.name.lower()
                
                # Match content to placeholders
                if 'title' in ph_name and 'title' in content:
                    placeholder.text = content['title']
                elif 'subtitle' in ph_name and 'subtitle' in content:
                    placeholder.text = content['subtitle']
                elif 'date' in ph_name and 'date' in content:
                    placeholder.text = content['date']
                elif 'heading' in ph_name and 'headings' in content:
                    # Match heading by index
                    heading_num = self._extract_number(ph_name)
                    headings = content['headings']
                    if isinstance(headings, list) and heading_num < len(headings):
                        placeholder.text = headings[heading_num]
                elif 'content' in ph_name or 'text' in ph_name:
                    if 'bullets' in content:
                        self._add_bullets(placeholder, content['bullets'])
                    elif 'content' in content:
                        if isinstance(content['content'], list):
                            self._add_bullets(placeholder, content['content'])
                        else:
                            placeholder.text = str(content['content'])
                elif 'picture' in ph_name.lower() and 'image' in content:
                    # Add placeholder image
                    img_desc = content['image']
                    img_io = self.create_placeholder_image(img_desc)
                    placeholder.insert_picture(img_io)
                elif 'quote' in ph_name and 'quote' in content:
                    placeholder.text = content['quote']
                elif 'name' in ph_name and 'attribution' in content:
                    placeholder.text = content['attribution']
        
        # Save presentation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Extendicare_Presentation_{timestamp}.pptx"
        output_path = self.output_dir / filename
        prs.save(str(output_path))
        
        return str(output_path)
    
    def _parse_presentation_spec(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse different input formats into slide data"""
        # Handle different input formats
        if 'slides' in spec:
            # Explicit slides array
            return spec['slides']
        elif 'markdown' in spec:
            # Parse markdown format
            return self._parse_markdown(spec['markdown'])
        elif 'description' in spec:
            # Natural language - would need NLP, for now just create basic slides
            return self._parse_natural_language(spec['description'])
        else:
            # Assume spec is a single slide
            return [spec]
    
    def _parse_markdown(self, markdown: str) -> List[Dict[str, Any]]:
        """Parse markdown into slides"""
        slides = []
        current_slide = None
        
        lines = markdown.strip().split('\n')
        for line in lines:
            if line.startswith('# '):
                # New slide with title
                if current_slide:
                    slides.append(current_slide)
                current_slide = {
                    'layout_index': 0,  # Title slide
                    'content': {'title': line[2:].strip()}
                }
            elif line.startswith('## '):
                # Subtitle or section header
                if current_slide:
                    current_slide['content']['subtitle'] = line[3:].strip()
                else:
                    current_slide = {
                        'layout_index': 5,  # 1 Column
                        'content': {'title': line[3:].strip()}
                    }
            elif line.startswith('- '):
                # Bullet point
                if not current_slide:
                    current_slide = {'layout_index': 5, 'content': {}}
                if 'bullets' not in current_slide['content']:
                    current_slide['content']['bullets'] = []
                current_slide['content']['bullets'].append(line[2:].strip())
        
        if current_slide:
            slides.append(current_slide)
        
        return slides
    
    def _parse_natural_language(self, description: str) -> List[Dict[str, Any]]:
        """Basic parsing of natural language description"""
        # This is a simplified version - in production, you'd use NLP
        slides = []
        
        # Create a title slide
        slides.append({
            'layout_index': 0,
            'content': {
                'title': 'Presentation',
                'subtitle': 'Generated from description',
                'date': datetime.now().strftime("%B %d, %Y")
            }
        })
        
        # Add a content slide
        slides.append({
            'layout_index': 5,
            'content': {
                'title': 'Content',
                'content': description
            }
        })
        
        return slides
    
    def _add_bullets(self, placeholder, bullets):
        """Add bullet points to a placeholder"""
        if hasattr(placeholder, 'text_frame'):
            text_frame = placeholder.text_frame
            text_frame.clear()  # Clear existing text
            
            for i, bullet in enumerate(bullets):
                if i == 0:
                    p = text_frame.paragraphs[0]
                else:
                    p = text_frame.add_paragraph()
                p.text = bullet
                p.level = 0
    
    def _extract_number(self, text: str) -> int:
        """Extract number from text (e.g., 'Heading 2' -> 1)"""
        import re
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) - 1 if numbers else 0

# MCP Server setup
server = Server("mcp-extendicare-ppt")

@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="query_layouts",
            description="Search for PowerPoint layouts by features",
            schema={
                "type": "object",
                "properties": {
                    "features": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Features to search for (e.g., 'chart', 'picture', '2 column')"
                    }
                }
            }
        ),
        Tool(
            name="get_layout_details",
            description="Get detailed information about a specific layout",
            schema={
                "type": "object",
                "properties": {
                    "layout_index": {
                        "type": "integer",
                        "description": "Index of the layout (0-21)"
                    }
                },
                "required": ["layout_index"]
            }
        ),
        Tool(
            name="create_presentation",
            description="Create a PowerPoint presentation with Extendicare branding",
            schema={
                "type": "object",
                "properties": {
                    "spec": {
                        "type": "object",
                        "description": "Presentation specification (supports multiple formats)"
                    }
                },
                "required": ["spec"]
            }
        )
    ]

# Global server instance
ppt_server = None

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> CallToolResult:
    global ppt_server
    
    if name == "query_layouts":
        features = arguments.get("features")
        results = await ppt_server.query_layouts(features)
        return CallToolResult(
            result=results,
            isError=False
        )
    
    elif name == "get_layout_details":
        layout_index = arguments["layout_index"]
        details = await ppt_server.get_layout_details(layout_index)
        return CallToolResult(
            result=details,
            isError=False
        )
    
    elif name == "create_presentation":
        spec = arguments["spec"]
        output_path = await ppt_server.create_presentation(spec)
        return CallToolResult(
            result={"success": True, "path": output_path},
            isError=False
        )
    
    else:
        return CallToolResult(
            result={"error": f"Unknown tool: {name}"},
            isError=True
        )

async def main():
    global ppt_server
    
    # Load config
    config = Config(
        template_path="path/to/your/Extendicare.pptx",  # UPDATE THIS
        output_dir="."
    )
    
    ppt_server = ExtendicarePPTServer(config)
    
    # Run the server
    async with server:
        await server.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. Create Configuration File for Claude Desktop

```json
# create file: config.json
{
  "template_path": "path/to/your/Extendicare.pptx",
  "output_dir": "."
}
```

### 5. Create Claude Desktop Integration

```json
# create file: claude_desktop_config.json
# This goes in ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "extendicare-ppt": {
      "command": "uv",
      "args": ["run", "python", "path/to/mcp-extendicare-ppt/mcp_server.py"],
      "env": {
        "PYTHONPATH": "path/to/mcp-extendicare-ppt"
      }
    }
  }
}
```

### 6. Create README with Examples

```markdown
# create file: README.md
# MCP Extendicare PPT Server

## Setup

1. Update `config.json` with your template path
2. Run the analysis script to verify template structure:
   ```bash
   uv run python analyze_template.py
   ```
3. Add to Claude Desktop config (see claude_desktop_config.json)

## Usage Examples

### Query available layouts
"Find all layouts with charts"
"Show me layouts that support 2 columns"

### Create presentations

#### Example 1: Structured format
```json
{
  "slides": [
    {
      "layout_index": 0,
      "content": {
        "title": "Q4 Results",
        "subtitle": "Financial Performance Review",
        "date": "March 2024"
      }
    },
    {
      "layout_index": 7,
      "content": {
        "title": "Key Metrics",
        "subtitle": "Year over Year Comparison",
        "bullets": [
          "Revenue up 15%",
          "EBITDA margin improved to 22%",
          "Operating costs reduced by 8%"
        ],
        "image": "Bar chart showing revenue growth"
      }
    }
  ]
}
```

#### Example 2: Markdown format
```markdown
# Q4 Financial Results
## Executive Summary

- Revenue exceeded targets
- Strong operational performance
- Positive outlook for Q1

## Key Metrics

- Revenue: $45.2M (+15% YoY)
- EBITDA: $9.9M (22% margin)
- Operating Costs: $28.1M (-8% YoY)
```

#### Example 3: Natural language
"Create a 5-slide presentation about Q4 results with an introduction, revenue overview, cost analysis, key achievements, and next steps"
```

### 7. Test the Server

```python
# create file: test_server.py
import asyncio
import json

async def test_server():
    # Test imports and basic functionality
    from mcp_server import ExtendicarePPTServer, Config
    
    config = Config(
        template_path="path/to/your/Extendicare.pptx",
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
```

## Development Steps

1. **First**: Update all paths in the files to point to your actual template
2. **Run**: `uv run python analyze_template.py` to verify template analysis
3. **Test**: `uv run python test_server.py` to test basic functionality
4. **Configure**: Add to Claude Desktop configuration
5. **Restart**: Restart Claude Desktop to load the MCP server

## Notes

- The server uses .pptx format (not .potx) as you mentioned
- Placeholder images are generated with descriptions for later replacement
- Supports multiple input formats for flexibility
- All generated presentations maintain Extendicare branding

## Troubleshooting

If the MCP server doesn't appear in Claude:
1. Check the logs in Claude Desktop
2. Verify all paths are correct
3. Ensure the template file is accessible
4. Try running the test script first
