# MCP Extendicare PPT Server

A Model Context Protocol (MCP) server that enables AI assistants to create PowerPoint presentations using the Extendicare branded template with intelligent layout selection.

## Features

- **22 Professionally Branded Layouts**: Title slides, divider slides, 1-4 column layouts, picture layouts, chart layouts, and table layouts
- **Intelligent Layout Selection**: AI can query layouts by features (e.g., "chart", "picture", "2 column")
- **Multiple Input Formats**: Supports structured JSON, Markdown, and natural language descriptions
- **Automatic Placeholder Mapping**: Smart content-to-placeholder matching
- **Generated Placeholder Images**: Creates descriptive placeholder images for later replacement

## Quick Start

### 1. Setup

```bash
# Clone or create the project
uv init
uv add python-pptx pillow mcp pydantic

# Verify template analysis
uv run python analyze_template.py
```

### 2. Test the Server

```bash
uv run python test_server.py
```

### 3. Add to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "extendicare-ppt": {
      "command": "uv",
      "args": ["run", "python", "/path/to/mcp-extendicare-ppt/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/mcp-extendicare-ppt"
      }
    }
  }
}
```

## Usage Examples

### Query Available Layouts

```
"Find all layouts with charts"
"Show me layouts that support 2 columns"
"What layouts have picture placeholders?"
```

### Create Presentations

#### Structured Format
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

#### Markdown Format
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

#### Natural Language
```
"Create a 5-slide presentation about Q4 results with an introduction, revenue overview, cost analysis, key achievements, and next steps"
```

## Available Layouts

| Index | Layout Name | Key Features |
|-------|-------------|--------------|
| 0-2 | Title Slides | Text only, Picture right/left |
| 3-4 | Divider Slides | Section breaks with/without pictures |
| 5-6 | 1 Column | With/without subheading |
| 7-8 | 2 Column | With/without subheadings |
| 9 | 2 Column Quote | Quote with attribution |
| 10-11 | 2 Column Pictures | Picture layouts with text |
| 12-13 | 3 Column | Subheadings and pictures |
| 14-15 | 4 Column | Maximum content density |
| 16 | Table Layout | Structured data presentation |
| 17-18 | Chart Layouts | Data visualization |
| 19-20 | Small Text | Dense content layouts |
| 21 | Blank Title | Maximum flexibility |

## Development

### Project Structure
```
mcp-extendicare-ppt/
   mcp_server.py          # Main MCP server
   analyze_template.py    # Template analysis tool
   test_server.py         # Testing script
   template_analysis.json # Layout metadata
   config.json           # Configuration
   claude_desktop_config.json # Claude Desktop setup
   README.md
```

### Testing
```bash
# Test template analysis
uv run python analyze_template.py

# Test server functionality  
uv run python test_server.py

# Test in Claude Desktop
# Add to configuration and restart Claude Desktop
```

## Troubleshooting

1. **Server doesn't appear in Claude**: Check Claude Desktop logs and verify paths
2. **Template not found**: Update paths in config.json and mcp_server.py
3. **Import errors**: Ensure all dependencies are installed with `uv add`
4. **Presentation creation fails**: Verify template file is accessible and not corrupted

## Contributing

When adding new features:
1. Update template analysis if layout changes
2. Add tests for new functionality
3. Update documentation
4. Test with Claude Desktop integration

## License

Internal Extendicare project - All rights reserved.