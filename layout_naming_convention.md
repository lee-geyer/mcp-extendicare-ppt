# AI-Friendly PowerPoint Template Naming Convention

## Overview
This document defines naming conventions for creating PowerPoint templates that are optimized for AI consumption and automation.

## Core Principles

1. **Semantic Over Generic**: Names should describe purpose, not just position
2. **Predictable Patterns**: Similar layouts should follow consistent naming
3. **Context Awareness**: Include information about content type and layout structure
4. **Machine Readable**: Use consistent delimiters and patterns

## Layout Naming Pattern

```
[ContentType]_[Structure]_[Specificity]
```

### Examples:
- `TitleSlide_TextOnly` (instead of "Title Slide")
- `TwoColumn_ChartText` (instead of "2 Column")
- `Dashboard_QuadMetrics` (instead of "4 Column")

## Placeholder Naming Pattern

```
[Purpose]_[Context]_[Position]
```

### Examples:
- `FinancialChart_Primary` (instead of "Chart Placeholder 1")
- `KeyInsights_Analysis` (instead of "Text Placeholder 2")
- `LeftColumn_Bullets` (instead of "Content Placeholder 3")

## Content Type Classifications

### Presentation Structure
- `TitleSlide_*` - Opening/section slides
- `DividerSlide_*` - Section breaks
- `ConclusionSlide_*` - Ending slides

### Content Categories
- `Narrative_*` - Text-heavy content
- `Dashboard_*` - Multiple data points
- `Comparison_*` - Side-by-side content
- `Gallery_*` - Image-focused layouts

### Data Visualization
- `SingleChart_*` - One primary chart
- `DualChart_*` - Two charts (comparison)
- `MetricGrid_*` - Multiple KPIs
- `Table_*` - Tabular data

## Placeholder Purpose Types

### Text Content
- `Title` - Main headings
- `Subtitle` - Secondary headings
- `Body` - Paragraph content
- `Bullets` - List content
- `Quote` - Quotation text
- `Analysis` - Data insights
- `Summary` - Key takeaways

### Data Content
- `Chart` - Charts and graphs
- `Table` - Data tables
- `Metric` - KPI displays
- `Gauge` - Progress indicators

### Media Content
- `Image` - Pictures
- `Logo` - Company branding
- `Icon` - Small graphics
- `Diagram` - Process flows

### Metadata
- `Date` - Date information
- `Footer` - Footer content
- `SlideNumber` - Pagination

## Position and Structure Indicators

### Column Layout
- `LeftColumn_*` - Left side content
- `RightColumn_*` - Right side content
- `CenterColumn_*` - Middle column
- `Grid_*` - Grid position (e.g., `Grid_TopLeft`)

### Priority Indicators
- `Primary` - Main/most important
- `Secondary` - Supporting content
- `Tertiary` - Additional details

### Content Relationship
- `MainChart_*` - Primary data visualization
- `SupportingText_*` - Text that explains charts
- `ComparisonLeft_*` - Left side of comparison
- `ComparisonRight_*` - Right side of comparison

## Example Template Structure

```json
{
  "TitleSlide_TextOnly": {
    "placeholders": {
      "PresentationTitle_Primary": "Main title",
      "PresentationSubtitle_Context": "Supporting subtitle", 
      "EventDate_Footer": "Date/event info"
    }
  },
  "Dashboard_DualChart": {
    "placeholders": {
      "DashboardTitle_Primary": "Dashboard heading",
      "LeftChart_Revenue": "Revenue chart",
      "LeftChart_Analysis": "Revenue insights",
      "RightChart_Costs": "Cost chart", 
      "RightChart_Analysis": "Cost insights"
    }
  }
}
```

## Benefits for AI/MCP Integration

1. **Intent Recognition**: AI can understand placeholder purpose from name
2. **Content Matching**: Automatic mapping of content type to appropriate placeholders
3. **Layout Selection**: Choose layouts based on content analysis
4. **Quality Assurance**: Validate content placement using semantic understanding
5. **Template Evolution**: Easy to extend and modify while maintaining consistency

## Implementation Guidelines

### For Template Creators
1. Start with content strategy, not visual design
2. Name placeholders before designing layout
3. Use the metadata file to document relationships
4. Test with automation tools
5. Include usage examples

### For Developers
1. Parse semantic names to understand structure
2. Use metadata for intelligent layout selection
3. Validate content against guidelines
4. Provide helpful error messages
5. Support flexible content mapping

## Migration Strategy

### From Existing Templates
1. Analyze current placeholder usage patterns
2. Create semantic mapping
3. Generate metadata file
4. Test with existing content
5. Gradually adopt new naming

### Quality Assurance
- Consistent naming across similar layouts
- All placeholders have semantic names
- Metadata accurately reflects structure
- Content guidelines are clear and actionable
- AI can successfully parse and use the template