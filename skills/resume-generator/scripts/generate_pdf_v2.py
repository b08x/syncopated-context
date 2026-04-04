#!/usr/bin/env python3
"""
Enhanced Resume PDF Generator with Dynamic Page Break Detection

Analyzes HTML content structure to intelligently place page breaks, preventing
sections from being split awkwardly. Uses content measurement and logical
grouping to determine optimal break points.

Usage:
    python3 generate_pdf_v2.py input.html output.pdf
"""

import sys
import argparse
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import subprocess

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError:
    print("Error: WeasyPrint not installed. Install with:")
    print("  pip install weasyprint --break-system-packages")
    sys.exit(1)


@dataclass
class ContentBlock:
    """Represents a logical content unit for page break analysis"""
    tag: str
    element_id: str
    content_type: str  # 'header', 'summary', 'section', 'entry', 'list_item'
    estimated_height: float  # in points
    priority: int  # higher = keep together more strongly
    parent_section: Optional[str] = None
    can_break_before: bool = True
    can_break_after: bool = True


class PageBreakAnalyzer:
    """Analyzes HTML content structure to determine optimal page break positions"""

    # Page dimensions for US Letter in points (72 DPI)
    PAGE_HEIGHT = 11 * 72  # 792 points
    PAGE_MARGIN_TOP = 0.6 * 72  # 43.2 points
    PAGE_MARGIN_BOTTOM = 0.7 * 72  # 50.4 points
    USABLE_HEIGHT = PAGE_HEIGHT - PAGE_MARGIN_TOP - PAGE_MARGIN_BOTTOM  # ~698 points

    # Estimated heights in points for different elements
    ELEMENT_HEIGHTS = {
        'h1': 24,
        'h2': 18,
        'h3': 14,
        'h4': 12,
        'p': 14,
        'li': 14,
        'div.contact': 12,
        'div.summary': 16,
        'div.entry-header': 16,
        'div.entry': 20,  # base height, plus content
        'ul': 4,  # container overhead
        'section': 8,  # container overhead
    }

    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.content_blocks: List[ContentBlock] = []
        self.current_height = 0

    def analyze_content(self) -> List[ContentBlock]:
        """Analyze HTML structure and identify content blocks"""
        self.content_blocks = []
        self._analyze_element(self.soup.body)
        return self.content_blocks

    def _analyze_element(self, element, parent_section: str = None, depth: int = 0):
        """Recursively analyze elements to build content block list"""
        if not element or not hasattr(element, 'name'):
            return

        tag_name = element.name
        if not tag_name:
            return

        # Skip script, style, and other non-content elements
        if tag_name in ['script', 'style', 'meta', 'link']:
            return

        element_id = element.get('id', f'{tag_name}_{len(self.content_blocks)}')

        # Determine content type and properties
        content_type, priority, can_break_before, can_break_after = self._classify_element(element, parent_section)

        # Estimate content height
        height = self._estimate_element_height(element, tag_name)

        if height > 0 or content_type in ['section', 'entry']:
            block = ContentBlock(
                tag=tag_name,
                element_id=element_id,
                content_type=content_type,
                estimated_height=height,
                priority=priority,
                parent_section=parent_section,
                can_break_before=can_break_before,
                can_break_after=can_break_after
            )
            self.content_blocks.append(block)

        # Update parent section for child elements
        new_parent = parent_section
        if content_type == 'section':
            new_parent = element_id

        # Recursively analyze children
        for child in element.children:
            self._analyze_element(child, new_parent, depth + 1)

    def _classify_element(self, element, parent_section: str) -> Tuple[str, int, bool, bool]:
        """Classify element type and determine break constraints"""
        tag = element.name
        classes = element.get('class', [])

        # Header elements
        if tag == 'header' or 'header' in classes:
            return 'header', 100, False, False  # Never break header

        # Summary/intro sections
        if 'summary' in classes or tag == 'summary':
            return 'summary', 90, True, False  # Can break before, not after

        # Main sections (Experience, Education, etc.)
        if tag == 'section':
            return 'section', 80, True, True

        # Individual experience/education entries
        if 'entry' in classes:
            return 'entry', 85, True, False  # Keep entry together

        # Entry headers (job title, dates)
        if 'entry-header' in classes:
            return 'entry_header', 95, True, False  # Don't separate from content

        # List items
        if tag == 'li':
            return 'list_item', 70, False, True  # Prefer to keep with list

        # Section headers
        if tag in ['h1', 'h2', 'h3']:
            priority = {'h1': 100, 'h2': 90, 'h3': 85}[tag]
            return 'heading', priority, True, False  # Don't orphan headings

        # Regular content
        return 'content', 50, True, True

    def _estimate_element_height(self, element, tag_name: str) -> float:
        """Estimate the rendered height of an element in points"""
        classes = element.get('class', [])

        # Get base height from element type
        height = self.ELEMENT_HEIGHTS.get(tag_name, 14)

        # Adjust for classes
        for cls in classes:
            class_key = f'{tag_name}.{cls}'
            if class_key in self.ELEMENT_HEIGHTS:
                height = self.ELEMENT_HEIGHTS[class_key]
                break

        # Add height for text content
        text_content = element.get_text().strip()
        if text_content:
            # Estimate based on character count (rough approximation)
            line_chars = 80  # Approximate characters per line
            lines = max(1, len(text_content) / line_chars)
            height += (lines - 1) * 14  # Additional lines

        # Add height for child elements if this is a container
        if tag_name in ['div', 'section', 'ul', 'ol']:
            for child in element.children:
                if hasattr(child, 'name') and child.name:
                    height += self._estimate_element_height(child, child.name) * 0.3

        return height

    def generate_break_points(self) -> List[str]:
        """Generate CSS selectors where page breaks should be allowed/encouraged"""
        break_points = []
        current_page_height = 0

        for i, block in enumerate(self.content_blocks):
            # Check if adding this block would overflow the page
            if current_page_height + block.estimated_height > self.USABLE_HEIGHT:
                # Look for optimal break point
                break_selector = self._find_break_point(i)
                if break_selector:
                    break_points.append(break_selector)
                    current_page_height = block.estimated_height
                else:
                    current_page_height += block.estimated_height
            else:
                current_page_height += block.estimated_height

        return break_points

    def _find_break_point(self, current_index: int) -> Optional[str]:
        """Find the best place to insert a page break before current_index"""
        # Look backward for suitable break points
        for i in range(current_index - 1, max(-1, current_index - 5), -1):
            if i < 0:
                break

            block = self.content_blocks[i]

            # Can we break after this block?
            if block.can_break_after and block.priority < 90:
                next_block = self.content_blocks[i + 1] if i + 1 < len(self.content_blocks) else None

                # Can we break before the next block?
                if next_block and next_block.can_break_before:
                    # Generate CSS selector
                    return f"#{block.element_id}"

        return None


def generate_dynamic_css(html_content: str) -> str:
    """Generate CSS with intelligent page break rules based on content analysis"""
    analyzer = PageBreakAnalyzer(html_content)
    blocks = analyzer.analyze_content()
    break_points = analyzer.generate_break_points()

    # Base page break CSS
    css_rules = [
        """
/* Dynamic page break rules */
@page {
    size: letter portrait;
    margin: 0.6in 0.7in;
    orphans: 3;
    widows: 3;
}

/* Prevent breaking inside critical elements */
header, .summary, .entry, .entry-header {
    page-break-inside: avoid;
    break-inside: avoid;
}

/* Section headers shouldn't be orphaned */
h1, h2, h3 {
    page-break-after: avoid;
    break-after: avoid;
    orphans: 3;
    widows: 3;
}

/* Default list handling */
li {
    page-break-inside: avoid;
    break-inside: avoid;
}

/* Skills sections should stay together */
.skills-category, .skills-list, .skills-grid {
    page-break-inside: avoid;
    break-inside: avoid;
}
"""
    ]

    # Add specific break points
    for selector in break_points:
        css_rules.append(f"""
{selector} {{
    page-break-after: always;
    break-after: page;
}}
""")

    # Add high-priority keep-together rules
    high_priority_blocks = [b for b in blocks if b.priority > 85]
    for block in high_priority_blocks:
        css_rules.append(f"""
#{block.element_id} {{
    page-break-inside: avoid;
    break-inside: avoid;
}}
""")

    return "\n".join(css_rules)


def inject_dynamic_css(html_content: str) -> str:
    """Inject dynamically generated CSS into HTML content"""
    dynamic_css = generate_dynamic_css(html_content)

    if '</style>' in html_content:
        # Insert before closing style tag
        return html_content.replace('</style>', f'\n{dynamic_css}\n</style>')
    elif '<head>' in html_content:
        # Add style tag in head
        style_block = f'<style>\n{dynamic_css}\n</style>'
        return html_content.replace('<head>', f'<head>\n{style_block}\n')
    else:
        # Fallback: prepend to body
        print("Warning: No <head> or <style> found, CSS may not apply correctly")
        return html_content


def generate_pdf(html_path: Path, pdf_path: Path, use_dynamic_breaks: bool = True) -> bool:
    """
    Generate PDF from HTML resume with intelligent page breaks.

    Args:
        html_path: Path to input HTML file
        pdf_path: Path to output PDF file
        use_dynamic_breaks: Whether to use dynamic page break detection

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read HTML content
        html_content = html_path.read_text(encoding='utf-8')

        # Apply dynamic page break CSS if requested
        if use_dynamic_breaks:
            print("Analyzing content structure for optimal page breaks...")
            html_content = inject_dynamic_css(html_content)

        # Generate PDF
        print(f"Generating PDF: {pdf_path}")

        # Create font configuration for better rendering
        font_config = FontConfiguration()

        HTML(string=html_content, base_url=str(html_path.parent)).write_pdf(
            pdf_path,
            font_config=font_config,
            presentational_hints=True
        )

        print(f"✓ PDF generated successfully: {pdf_path}")
        print(f"  Size: {pdf_path.stat().st_size / 1024:.1f} KB")
        return True

    except Exception as e:
        print(f"✗ Error generating PDF: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate PDF from HTML resume with intelligent page breaks'
    )
    parser.add_argument('input', type=Path, help='Input HTML file')
    parser.add_argument('output', type=Path, help='Output PDF file')
    parser.add_argument(
        '--no-dynamic-breaks',
        action='store_true',
        help='Disable dynamic page break analysis (use static CSS only)'
    )

    args = parser.parse_args()

    # Validate input
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if not args.input.suffix.lower() == '.html':
        print(f"Warning: Input file does not have .html extension: {args.input}")

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Generate PDF
    success = generate_pdf(
        args.input,
        args.output,
        use_dynamic_breaks=not args.no_dynamic_breaks
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
