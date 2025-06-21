#!/usr/bin/env python3
"""
Intelligent Layout Selector for AI-Friendly PowerPoint Templates
Uses semantic analysis to recommend optimal layouts based on content
"""
import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ContentAnalysis:
    """Analysis results for input content"""
    content_type: str
    has_charts: bool
    has_tables: bool
    has_images: bool
    text_density: str  # low, medium, high
    structure: str  # single_topic, comparison, list, narrative
    data_points: int
    key_metrics: List[str]
    

class SmartLayoutSelector:
    """Intelligent layout selection based on content analysis"""
    
    def __init__(self, metadata_path: str = "ai_friendly_template_metadata.json"):
        """Initialize with template metadata"""
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        
        self.layouts = self.metadata['layouts']
        self.content_mapping = self.metadata['content_to_layout_mapping']
        
    def analyze_content(self, content: Dict) -> ContentAnalysis:
        """Analyze input content to determine characteristics"""
        
        # Extract text content
        all_text = ""
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, str):
                    all_text += value + " "
                elif isinstance(value, list):
                    all_text += " ".join(str(item) for item in value) + " "
        elif isinstance(content, str):
            all_text = content
        
        # Analyze content characteristics
        has_charts = any(keyword in all_text.lower() for keyword in 
                        ['chart', 'graph', 'revenue', 'growth', 'trend', 'data', 'metric', 'kpi'])
        
        has_tables = any(keyword in all_text.lower() for keyword in 
                        ['table', 'comparison', 'vs', 'versus', 'compare'])
        
        has_images = any(keyword in all_text.lower() for keyword in 
                        ['image', 'photo', 'picture', 'visual', 'diagram'])
        
        # Determine text density
        word_count = len(all_text.split())
        if word_count < 20:
            text_density = "low"
        elif word_count < 100:
            text_density = "medium" 
        else:
            text_density = "high"
        
        # Determine structure
        structure = self._analyze_structure(content, all_text)
        
        # Count data points
        data_points = self._count_data_points(all_text)
        
        # Extract key metrics
        key_metrics = self._extract_metrics(all_text)
        
        # Determine content type
        content_type = self._determine_content_type(has_charts, has_tables, text_density, structure)
        
        return ContentAnalysis(
            content_type=content_type,
            has_charts=has_charts,
            has_tables=has_tables,
            has_images=has_images,
            text_density=text_density,
            structure=structure,
            data_points=data_points,
            key_metrics=key_metrics
        )
    
    def _analyze_structure(self, content: Dict, text: str) -> str:
        """Determine content structure"""
        if isinstance(content, dict):
            keys = list(content.keys())
            
            # Look for comparison indicators
            if any(key in ['left', 'right', 'before', 'after', 'vs'] for key in keys):
                return "comparison"
            
            # Look for list structure
            if any(isinstance(value, list) for value in content.values()):
                return "list"
        
        # Analyze text patterns
        if any(word in text.lower() for word in ['versus', 'compared to', 'vs', 'while']):
            return "comparison"
        elif any(word in text.lower() for word in ['first', 'second', 'third', 'finally']):
            return "list"
        elif len(text.split('.')) > 3:
            return "narrative"
        else:
            return "single_topic"
    
    def _count_data_points(self, text: str) -> int:
        """Count potential data points in content"""
        # Look for numbers, percentages, currency
        numbers = re.findall(r'\d+\.?\d*%?|\$\d+', text)
        return len(numbers)
    
    def _extract_metrics(self, text: str) -> List[str]:
        """Extract key metrics mentioned in text"""
        metrics = []
        metric_keywords = [
            'revenue', 'profit', 'ebitda', 'growth', 'margin', 'roi', 'kpi',
            'cost', 'efficiency', 'utilization', 'occupancy', 'satisfaction'
        ]
        
        for keyword in metric_keywords:
            if keyword in text.lower():
                metrics.append(keyword)
        
        return metrics
    
    def _determine_content_type(self, has_charts: bool, has_tables: bool, 
                               text_density: str, structure: str) -> str:
        """Determine overall content type"""
        if has_charts and has_tables:
            return "dashboard"
        elif has_charts:
            return "data_visualization"
        elif has_tables:
            return "data_table"
        elif text_density == "high":
            return "narrative"
        elif structure == "comparison":
            return "comparison"
        elif structure == "list":
            return "bullet_points"
        else:
            return "general_content"
    
    def recommend_layouts(self, content: Dict, top_n: int = 3) -> List[Tuple[str, float, str]]:
        """Recommend best layouts for given content with confidence scores"""
        analysis = self.analyze_content(content)
        recommendations = []
        
        for layout_id, layout_info in self.layouts.items():
            score = self._calculate_layout_score(analysis, layout_info)
            reason = self._generate_recommendation_reason(analysis, layout_info, score)
            recommendations.append((layout_id, score, reason))
        
        # Sort by score and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_n]
    
    def _calculate_layout_score(self, analysis: ContentAnalysis, layout_info: Dict) -> float:
        """Calculate how well a layout matches the content"""
        score = 0.0
        
        # Category matching
        category = layout_info.get('category', '')
        if analysis.content_type == 'data_visualization' and category == 'data_visualization':
            score += 3.0
        elif analysis.content_type == 'narrative' and category == 'content':
            score += 3.0
        elif analysis.content_type == 'dashboard' and 'dashboard' in layout_info.get('subcategory', ''):
            score += 3.0
        
        # Structure matching
        structure = layout_info.get('structure', '')
        if analysis.structure == 'comparison' and 'two_column' in structure:
            score += 2.0
        elif analysis.structure == 'single_topic' and 'single_column' in structure:
            score += 2.0
        
        # Chart requirements
        placeholders = layout_info.get('placeholders', {})
        chart_placeholders = sum(1 for p in placeholders.values() if p.get('type') == 'chart')
        
        if analysis.has_charts:
            if chart_placeholders > 0:
                score += 2.0
            if analysis.data_points > 5 and chart_placeholders >= 2:
                score += 1.0
        elif chart_placeholders > 0:
            score -= 1.0  # Penalty for chart layouts without chart content
        
        # Text density considerations
        text_placeholders = sum(1 for p in placeholders.values() if p.get('type') in ['body', 'bullets'])
        
        if analysis.text_density == 'high' and text_placeholders >= 2:
            score += 1.0
        elif analysis.text_density == 'low' and text_placeholders == 1:
            score += 1.0
        
        # Use case matching
        use_cases = layout_info.get('use_cases', [])
        if analysis.content_type in [case.replace(' ', '_') for case in use_cases]:
            score += 1.0
        
        return score
    
    def _generate_recommendation_reason(self, analysis: ContentAnalysis, 
                                      layout_info: Dict, score: float) -> str:
        """Generate human-readable reason for recommendation"""
        reasons = []
        
        layout_name = layout_info.get('semantic_name', 'Unknown Layout')
        
        if score >= 3.0:
            reasons.append(f"Perfect match for {analysis.content_type}")
        elif score >= 2.0:
            reasons.append(f"Good fit for {analysis.content_type}")
        elif score >= 1.0:
            reasons.append(f"Suitable for {analysis.content_type}")
        else:
            reasons.append("Partial match")
        
        if analysis.has_charts:
            chart_count = sum(1 for p in layout_info.get('placeholders', {}).values() 
                            if p.get('type') == 'chart')
            if chart_count > 0:
                reasons.append(f"Supports {chart_count} chart(s)")
        
        if analysis.structure == 'comparison' and 'two_column' in layout_info.get('structure', ''):
            reasons.append("Ideal for comparisons")
        
        return f"{layout_name}: {', '.join(reasons)}"
    
    def get_layout_details(self, layout_id: str) -> Dict:
        """Get detailed information about a specific layout"""
        if layout_id not in self.layouts:
            return {"error": f"Layout {layout_id} not found"}
        
        layout = self.layouts[layout_id]
        
        # Enhance with semantic information
        enhanced_layout = layout.copy()
        enhanced_layout['ai_optimized'] = True
        enhanced_layout['placeholder_summary'] = self._summarize_placeholders(layout)
        
        return enhanced_layout
    
    def _summarize_placeholders(self, layout: Dict) -> Dict:
        """Create a summary of placeholders by type"""
        placeholders = layout.get('placeholders', {})
        summary = {
            'total_count': len(placeholders),
            'by_type': {},
            'by_column': {},
            'required_count': 0
        }
        
        for placeholder_info in placeholders.values():
            # Count by type
            ptype = placeholder_info.get('type', 'unknown')
            summary['by_type'][ptype] = summary['by_type'].get(ptype, 0) + 1
            
            # Count by column
            column = placeholder_info.get('column', 'none')
            summary['by_column'][column] = summary['by_column'].get(column, 0) + 1
            
            # Count required
            if placeholder_info.get('required', False):
                summary['required_count'] += 1
        
        return summary

def test_smart_selector():
    """Test the smart layout selector with sample content"""
    selector = SmartLayoutSelector()
    
    # Test cases
    test_cases = [
        {
            "name": "Financial Dashboard",
            "content": {
                "title": "Q3 Financial Results",
                "revenue_chart": "Revenue grew 15% to $45M",
                "cost_analysis": "Costs reduced by 8% through efficiency gains",
                "metrics": ["revenue: $45M", "growth: 15%", "margin: 22%"]
            }
        },
        {
            "name": "Executive Summary", 
            "content": {
                "title": "Strategic Overview",
                "summary": "This quarter we achieved significant milestones in our expansion strategy. Our new facilities are performing above expectations, and customer satisfaction has increased substantially. We are well-positioned for continued growth in Q4 and beyond."
            }
        },
        {
            "name": "Comparison Analysis",
            "content": {
                "title": "Before vs After Implementation", 
                "left_side": "Previous process took 5 days and cost $10K",
                "right_side": "New process takes 2 days and costs $6K",
                "conclusion": "60% faster and 40% cheaper"
            }
        }
    ]
    
    print("🧠 Smart Layout Selector Test Results\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print("-" * 50)
        
        analysis = selector.analyze_content(test_case['content'])
        print(f"Content Analysis:")
        print(f"  Type: {analysis.content_type}")
        print(f"  Structure: {analysis.structure}")
        print(f"  Text Density: {analysis.text_density}")
        print(f"  Has Charts: {analysis.has_charts}")
        print(f"  Data Points: {analysis.data_points}")
        
        recommendations = selector.recommend_layouts(test_case['content'])
        print(f"\nTop Recommendations:")
        
        for j, (layout_id, score, reason) in enumerate(recommendations, 1):
            layout_name = selector.layouts[layout_id].get('semantic_name', f'Layout {layout_id}')
            print(f"  {j}. {layout_name} (Score: {score:.1f})")
            print(f"     {reason}")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_smart_selector()