# Resume Generator Page Break Improvements

## Summary of Changes

The resume generator skill has been enhanced with **dynamic page break detection** to solve the problem of sections being split awkwardly in PDF output.

## Key Improvements

### 1. Enhanced PDF Generation (`generate_pdf_v2.py`)

**Problem Solved:** The original static CSS approach used generic rules that couldn't adapt to different content structures, resulting in job entries and sections being broken across pages inappropriately.

**Solution:** Dynamic content analysis that:
- Parses HTML structure using BeautifulSoup
- Identifies logical content units (headers, sections, job entries, skills)
- Estimates element heights based on actual content
- Calculates optimal page break positions
- Generates targeted CSS rules specific to the content

### 2. Content-Aware Break Points

**New Features:**
- **ContentBlock dataclass**: Represents logical units with break preferences and priorities
- **PageBreakAnalyzer class**: Analyzes structure and determines optimal breaks
- **Priority system**: Higher priority elements (headers, summaries) get stronger protection
- **Height estimation**: Uses content length and styling to predict page overflow

### 3. Intelligent CSS Generation

**Previous:** Static CSS rules applied to all resumes
```css
.entry { page-break-inside: avoid; }
section { page-break-after: avoid; }
```

**New:** Dynamic CSS tailored to specific content structure
```css
#entry_2 { page-break-after: always; }
#section_experience { page-break-inside: avoid; }
```

### 4. Dependencies & Environment

**Added Files:**
- `requirements.txt` - Comprehensive dependency list
- `generate_pdf_v2.py` - Enhanced PDF generator with dynamic analysis
- `test_page_breaks.py` - Comparison testing script
- `evals/evals.json` - Test cases for skill evaluation

**Dependencies:**
- `weasyprint>=60.0` - PDF generation
- `beautifulsoup4>=4.12.0` - HTML parsing
- `lxml>=4.9.0` - XML processing
- `fonttools>=4.33.0` - Enhanced font support

## Usage

### Enhanced Method (Recommended)
```bash
python3 scripts/generate_pdf_v2.py resume.html resume.pdf
```

### Legacy Method (Still Available)
```bash
python3 scripts/generate_pdf.py resume.html resume.pdf
```

## Technical Details

### Content Analysis Process

1. **Parse HTML Structure**: BeautifulSoup extracts semantic elements
2. **Classify Elements**: Determine content type (header, section, entry, etc.) and priority
3. **Estimate Heights**: Calculate rendered height based on content and styling
4. **Find Break Points**: Identify optimal page break locations using height estimation
5. **Generate CSS**: Create targeted rules for specific elements

### Priority Levels

- **100**: Headers and critical contact info (never break)
- **95**: Entry headers (job titles + dates - don't separate from content)
- **90**: Summaries and section headers (avoid breaking after)
- **85**: Job/education entries (keep together)
- **80**: Main sections (can break but prefer not to)
- **70**: List items (prefer to keep with list)
- **50**: Regular content (flexible)

## Benefits

✅ **Eliminates awkward page breaks** in job entries and sections
✅ **Preserves logical content groupings** (skills categories, experience entries)
✅ **Adapts to different content lengths** automatically
✅ **Maintains professional appearance** across all resume lengths
✅ **Backward compatible** with existing templates and workflows

## Testing

The enhanced system has been tested with actual resume data and shows significant improvement in page break quality compared to static CSS rules. Test cases verify:

- Content structure preservation
- Dynamic analysis execution
- Professional template compatibility
- Side-by-side quality comparison

## Future Enhancements

Potential areas for further improvement:
- **Multi-column layout handling** for modern template
- **Widow/orphan optimization** for bullet points
- **Section size balancing** across pages
- **Template-specific break preferences**
