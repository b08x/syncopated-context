# Resume Generation Scripts Reference

This directory contains Python scripts for generating PDF and DOCX resumes with precise formatting and intelligent page breaks.

## Scripts

### generate_pdf.py

Converts HTML resumes to PDF using WeasyPrint with smart page-break handling.

**Features:**
- Automatic installation of WeasyPrint if needed
- Injects CSS rules to prevent awkward page breaks
- Preserves all HTML/CSS styling from templates
- Ensures section headers don't orphan
- Keeps work experience entries together

**Usage:**
```bash
# Basic usage
python3 generate_pdf.py input.html output.pdf

# Disable automatic page-break CSS injection
python3 generate_pdf.py --no-page-breaks input.html output.pdf
```

**Requirements:**
- WeasyPrint: `pip install weasyprint --break-system-packages`

**Page Break Behavior:**
- Work experience entries (`.entry`) never break mid-content
- Section headers (h2) never appear alone at bottom of page
- List items stay together when possible
- Minimum 3 lines kept together at page tops/bottoms (orphans/widows)
- Skills lists can break but individual items stay intact

---

### generate_docx.py

Generates Word documents from structured resume data with template-aware styling.

**Features:**
- Automatic installation of python-docx if needed
- Supports all four templates: minimal, professional, modern, executive
- Maps HTML template styles to Word formatting
- Customizable colors, fonts, and spacing
- Intelligent page break handling using Word's native features
- Proper heading hierarchy and styles

**Usage:**
```bash
# Basic usage
python3 generate_docx.py --data resume_data.json output.docx

# With template selection
python3 generate_docx.py --data resume_data.json --template professional output.docx

# With style customization
python3 generate_docx.py \
  --data resume_data.json \
  --template minimal \
  --accent-color "#2563eb" \
  --font-family serif \
  --font-size medium \
  --spacing normal \
  output.docx
```

**Requirements:**
- python-docx: `pip install python-docx --break-system-packages`

**Template Options:**
- `minimal` - Clean single-column, generous whitespace
- `professional` - Borders, section dividers, navy accents
- `modern` - Two-column layout (contact/skills in sidebar)
- `executive` - Traditional serif, conservative spacing

**Style Options:**

| Option | Values | Description |
|--------|--------|-------------|
| `--accent-color` | Hex color (e.g., `#2563eb`) | Color for headings and accents |
| `--font-family` | `system`, `serif`, `sans`, `mono` | Font family for entire document |
| `--font-size` | `small`, `medium`, `large` | Base font size (9pt, 10pt, 11pt) |
| `--spacing` | `compact`, `normal`, `relaxed` | Section and paragraph spacing |

---

## Resume Data Format

Both scripts expect resume data in a structured JSON format. See `examples/resume_data.json` for a complete example.

### Required Fields

```json
{
  "name": "Full Name"
}
```

### Contact Fields

```json
{
  "email": "email@example.com",
  "phone": "555-0100",
  "location": "City, ST",
  "linkedin": "linkedin.com/in/username",
  "portfolio": "https://example.com"
}
```

### Optional Summary

```json
{
  "summary": "2-3 sentence professional summary..."
}
```

### Experience Section

```json
{
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "date_range": "Jan 2020 – Present",
      "bullets": [
        "Achievement or responsibility",
        "Quantified impact with metrics",
        "Technologies and tools used"
      ]
    }
  ]
}
```

### Education Section

```json
{
  "education": [
    {
      "degree": "Bachelor of Science in Computer Science",
      "institution": "University Name",
      "year": 2020,
      "details": "Magna Cum Laude, GPA: 3.8/4.0"
    }
  ]
}
```

### Skills Section

Can be either categorized or a simple list:

**Categorized:**
```json
{
  "skills": {
    "Technical": ["Python", "JavaScript", "Docker", "AWS"],
    "Languages": ["English (Native)", "Spanish (Fluent)"],
    "Soft Skills": ["Leadership", "Communication", "Problem Solving"]
  }
}
```

**Simple List:**
```json
{
  "skills": ["Python", "JavaScript", "Docker", "AWS", "Leadership"]
}
```

### Projects Section

```json
{
  "projects": [
    {
      "title": "Project Name",
      "company": "Organization or Personal",
      "date_range": "2023",
      "bullets": [
        "Description of project",
        "Technologies used",
        "Impact or results"
      ]
    }
  ]
}
```

### Certifications Section

```json
{
  "certifications": [
    {
      "name": "AWS Certified Solutions Architect",
      "issuer": "Amazon Web Services",
      "date": "2023"
    }
  ]
}
```

---

## Programmatic Usage

Both scripts can be imported and used programmatically in Python code.

### PDF Generation

```python
from pathlib import Path
from generate_pdf import generate_pdf

html_path = Path("resume.html")
pdf_path = Path("resume.pdf")

success = generate_pdf(
    html_path,
    pdf_path,
    add_page_breaks=True  # Inject smart page-break CSS
)
```

### DOCX Generation

```python
from pathlib import Path
from generate_docx import ResumeGenerator, StyleConfig

# Configure style
style = StyleConfig(
    accent_color="#2563eb",
    font_family="system",
    font_size="medium",
    spacing="normal",
    page_size="letter"
)

# Create generator
generator = ResumeGenerator(template='minimal', style=style)

# Generate document
resume_data = {
    "name": "John Doe",
    "email": "john@example.com",
    # ... rest of resume data
}

output_path = Path("resume.docx")
success = generator.generate(resume_data, output_path)
```

---

## Workflow Examples

### HTML → PDF

```bash
# 1. Generate HTML from resume data (using skill)
# 2. Convert HTML to PDF with smart page breaks
python3 scripts/generate_pdf.py resume_john_doe.html resume_john_doe.pdf
```

### Direct to DOCX

```bash
# Generate DOCX directly from structured data
python3 scripts/generate_docx.py \
  --data resume_data.json \
  --template professional \
  --accent-color "#1e3a5f" \
  resume_john_doe.docx
```

### Job-Tailored Versions

```bash
# Generate multiple tailored versions
python3 scripts/generate_docx.py \
  --data resume_data_acme.json \
  --template minimal \
  resume_john_doe_acme.docx

python3 scripts/generate_docx.py \
  --data resume_data_techcorp.json \
  --template professional \
  resume_john_doe_techcorp.docx
```

---

## Troubleshooting

### WeasyPrint Installation Issues

If WeasyPrint fails to install, ensure you have system dependencies:

**macOS:**
```bash
brew install pango cairo gdk-pixbuf libffi
pip install weasyprint --break-system-packages
```

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
pip install weasyprint --break-system-packages
```

### python-docx Issues

If python-docx installation fails:
```bash
pip install --upgrade pip
pip install python-docx --break-system-packages
```

### Page Break Problems

If PDF page breaks still look awkward:
1. Check that your HTML uses semantic class names (`.entry`, `.entry-header`, etc.)
2. Ensure sections use `<section>` and `<h2>` tags
3. Consider adjusting spacing in the template's CSS
4. Use `--no-page-breaks` flag and add custom CSS rules

### DOCX Formatting Issues

If DOCX formatting doesn't match expectations:
1. Verify your JSON data structure matches the expected format
2. Check that style values are valid (e.g., hex colors start with `#`)
3. Try a different template if the current one doesn't suit your needs
4. Open the generated DOCX and manually adjust styles as needed

---

## Future Enhancements

Potential improvements to consider:

- **LaTeX support** - Generate LaTeX source for academic CVs
- **ATS optimization** - Parser-friendly formatting mode
- **Multi-page templates** - Dedicated styles for 2+ page resumes
- **Cover letter generation** - Companion scripts for cover letters
- **Batch processing** - Generate multiple versions from a single data source
- **Template customization** - User-defined templates via config files
