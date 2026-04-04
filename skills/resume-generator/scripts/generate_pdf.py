#!/usr/bin/env python3
"""
Resume PDF Generator

Converts HTML resumes to PDF with intelligent page break handling.
Uses WeasyPrint for high-quality PDF rendering with CSS support.

Usage:
    python3 generate_pdf.py input.html output.pdf
"""

import sys
import argparse
from pathlib import Path
try:
    from weasyprint import HTML, CSS
except ImportError:
    print("Error: WeasyPrint not installed. Install with:")
    print("  pip install weasyprint --break-system-packages")
    sys.exit(1)


# CSS rules for smart page breaks
PAGE_BREAK_CSS = """
/* Prevent awkward page breaks */
.entry {
    page-break-inside: avoid;
    break-inside: avoid;
}

section {
    page-break-after: avoid;
    break-after: avoid;
}

section h2 {
    page-break-after: avoid;
    break-after: avoid;
    orphans: 3;
    widows: 3;
}

.entry-header {
    page-break-after: avoid;
    break-after: avoid;
}

/* Keep list items together when possible */
.entry ul {
    page-break-inside: auto;
    break-inside: auto;
}

.entry li {
    page-break-inside: avoid;
    break-inside: avoid;
}

/* Prevent section headers from being orphaned */
h2 {
    orphans: 3;
    widows: 3;
}

/* Summary and header should not break */
header, .summary {
    page-break-after: avoid;
    break-after: avoid;
}

/* Sidebar handling for two-column layouts */
.sidebar {
    page-break-inside: avoid;
    break-inside: avoid;
}

/* Skills lists - allow breaks but keep items together */
.skills-list, .skills-grid {
    page-break-inside: auto;
    break-inside: auto;
}

.skills-list li, .skill-tag {
    page-break-inside: avoid;
    break-inside: avoid;
}

/* Ensure adequate spacing before page breaks */
section {
    margin-bottom: 1.5rem;
}

/* Keep minimum content at bottom of page before breaking */
@page {
    orphans: 3;
    widows: 3;
}
"""


def inject_page_break_css(html_content: str) -> str:
    """
    Inject page break CSS into the HTML content.
    
    Looks for </style> tag and inserts the page break rules before it.
    If no style tag exists, adds one in the head.
    """
    if '</style>' in html_content:
        # Insert before closing style tag
        return html_content.replace('</style>', f'\n{PAGE_BREAK_CSS}\n</style>')
    elif '<head>' in html_content:
        # Add style tag in head
        style_block = f'<style>\n{PAGE_BREAK_CSS}\n</style>'
        return html_content.replace('<head>', f'<head>\n{style_block}\n')
    else:
        # Fallback: prepend to body
        print("Warning: No <head> or <style> found, CSS may not apply correctly")
        return html_content


def generate_pdf(html_path: Path, pdf_path: Path, add_page_breaks: bool = True) -> bool:
    """
    Generate PDF from HTML resume.
    
    Args:
        html_path: Path to input HTML file
        pdf_path: Path to output PDF file
        add_page_breaks: Whether to inject smart page break CSS
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read HTML content
        html_content = html_path.read_text(encoding='utf-8')
        
        # Inject page break CSS if requested
        if add_page_breaks:
            html_content = inject_page_break_css(html_content)
        
        # Generate PDF
        print(f"Generating PDF: {pdf_path}")
        HTML(string=html_content, base_url=str(html_path.parent)).write_pdf(
            pdf_path,
            presentational_hints=True  # Respect HTML styling
        )
        
        print(f"✓ PDF generated successfully: {pdf_path}")
        print(f"  Size: {pdf_path.stat().st_size / 1024:.1f} KB")
        return True
        
    except Exception as e:
        print(f"✗ Error generating PDF: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate PDF from HTML resume with smart page breaks'
    )
    parser.add_argument('input', type=Path, help='Input HTML file')
    parser.add_argument('output', type=Path, help='Output PDF file')
    parser.add_argument(
        '--no-page-breaks',
        action='store_true',
        help='Disable smart page break CSS injection'
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
        add_page_breaks=not args.no_page_breaks
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
