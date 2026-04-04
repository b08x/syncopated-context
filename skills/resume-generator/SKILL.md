---
name: resume-generator
description: Generate tailored, professional resumes in multiple formats (Markdown, HTML, PDF, DOCX). Creates CVs, tailors to job descriptions, integrates GitHub repositories.
license: MIT
allowed-tools: Read Edit Grep Glob Bash Write
metadata:
  author: b08x
  version: "1.0.0"
  category: automation
---

# Resume Generator

Generate professional resumes from user-provided information, with optional job-description tailoring
and GitHub project enrichment.

## Modes of Operation

### 1. Baseline Resume

Collect professional information from the user and produce a general-purpose resume.

**Workflow:**
1. Gather resume content from the user (see Content Gathering below)
2. Optionally enrich with GitHub project data (see `references/github-integration.md`)
3. Select template and style configuration
4. Generate output in the requested format

### 2. Job-Tailored Resume

Take an existing baseline resume (or gather content fresh) plus a job description, then
reorder and emphasize sections to align with the target role.

**Workflow:**
1. Obtain or reuse resume content
2. Parse the job description for: required skills, preferred qualifications, key responsibilities, industry keywords
3. Score each resume section for relevance to the job description
4. Reorder sections and bullet points by relevance (highest-relevance items first)
5. Promote skills that match job requirements to prominent positions
6. Add a targeted summary/objective statement if not present
7. Generate output in the requested format

**Critical rule:** Do NOT fabricate, rewrite, or embellish the user's content. Only reorder,
emphasize, and restructure. The user's words and facts remain intact. If a mismatch exists
between the user's experience and the job, surface it rather than papering over it.

## Content Gathering

Collect the following sections from the user. Not all are required — adapt to what
the user provides. Ask focused follow-up questions for missing critical sections.

| Section | Priority | Notes |
|---------|----------|-------|
| Contact info | Required | Name, email, phone, location, LinkedIn/portfolio |
| Professional summary | Recommended | 2-3 sentence overview; generate if user approves |
| Work experience | Required | Title, company, dates, bullet points per role |
| Skills | Required | Technical and soft skills, tools, languages |
| Education | Required | Degree, institution, year, honors |
| Projects | Optional | Enrichable via GitHub MCP |
| Certifications | Optional | Name, issuing org, date |
| Publications | Optional | For academic/research roles |
| Volunteer work | Optional | |
| Awards/honors | Optional | |

When the user provides information conversationally (not structured), extract and organize
it into these sections. Confirm the organized structure before generating.

## Template System

Four built-in templates are available. Read `references/templates.md` for full template
definitions, HTML/CSS source, and customization parameters.

| Template | Description | Best For |
|----------|-------------|----------|
| `minimal` | Clean single-column, generous whitespace | Tech, startups, creative |
| `professional` | Subtle borders, section dividers, navy accents | Corporate, finance, consulting |
| `modern` | Two-column layout, sidebar for skills/contact | Design, marketing, product |
| `executive` | Traditional serif, conservative spacing | Senior leadership, government |

### Style Configuration

Each template accepts a style configuration object:

```
style:
  accent_color: "#2563eb"    # Primary accent (hex color)
  font_family: "system"      # system | serif | sans | mono
  font_size: "medium"        # small | medium | large
  spacing: "normal"          # compact | normal | relaxed
  page_size: "letter"        # letter | a4
```

If the user does not specify, use sensible defaults: `minimal` template, system font, medium
size, normal spacing, letter page size. Infer accent color from context if possible.

## Output Formats

### Markdown (.md)
Generate clean, well-structured markdown. Use `#` for name, `##` for sections, `###` for
job titles, and `-` for bullet points. Include a `---` separator between major sections.
Output directly — no external dependencies needed.

### HTML (.html)
Read `references/templates.md` for the full HTML template source. Generate a single
self-contained HTML file with embedded CSS. The HTML must render well in browsers and
print cleanly to PDF via browser print dialog.

### PDF (.pdf)
To generate PDF output with intelligent page breaks:
1. First generate the HTML version using the selected template
2. Use the enhanced `generate_pdf_v2.py` script (recommended) for dynamic page break detection:
   ```bash
   python3 scripts/generate_pdf_v2.py resume.html resume.pdf
   ```

The enhanced script features **dynamic content analysis** that:
- **Analyzes HTML structure** to identify logical content units (headers, sections, job entries, skills)
- **Estimates element heights** based on text content and styling
- **Calculates optimal page break positions** to prevent sections from splitting awkwardly
- **Generates targeted CSS rules** specific to your resume's content structure
- **Prevents orphaned headings** and keeps related content together
- **Preserves all HTML/CSS styling** while adding intelligent break points

**Key improvements over static CSS approach:**
- **Content-aware breaks**: Analyzes actual content rather than using generic rules
- **Logical grouping**: Keeps job entries, skill categories, and sections intact
- **Dynamic adaptation**: Adjusts break points based on content length and structure
- **Priority-based decisions**: Higher priority elements (headers, summaries) get stronger protection

**Dependencies:** Install with `pip install -r requirements.txt` or:
```bash
pip install weasyprint beautifulsoup4 --break-system-packages
```

**Options:**
- `--no-dynamic-breaks`: Disable dynamic analysis (use static CSS only)

**Legacy method:** The original `generate_pdf.py` script with static CSS rules is still available for compatibility.

**Fallback:** If WeasyPrint installation fails, the pdf skill at `/mnt/skills/public/pdf/SKILL.md` can be used as an alternative.

### DOCX (.docx)
To generate Word document output with precise template formatting:
1. Structure resume data as JSON (see data format below)
2. Use the `generate_docx.py` script:
   ```bash
   python3 scripts/generate_docx.py --data resume_data.json --template minimal output.docx
   ```

The script automatically:
- Installs python-docx if needed (`pip install python-docx --break-system-packages`)
- Maps template styles to Word formatting (colors, fonts, spacing)
- Creates properly formatted sections with consistent styling
- Handles page breaks intelligently using Word's native features
- Preserves the visual hierarchy of the selected template

**Template options:** `minimal`, `professional`, `modern`, `executive`

**Style customization:**
```bash
--accent-color "#2563eb"     # Hex color for headings/accents
--font-family serif          # system | serif | sans | mono
--font-size medium           # small | medium | large
--spacing normal             # compact | normal | relaxed
```

**Resume data format** (JSON):
```json
{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "555-0100",
  "location": "City, ST",
  "linkedin": "linkedin.com/in/username",
  "summary": "Professional summary text...",
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "date_range": "Jan 2020 – Present",
      "bullets": [
        "Achievement or responsibility",
        "Another achievement"
      ]
    }
  ],
  "education": [
    {
      "degree": "Degree Name",
      "institution": "University Name",
      "year": 2020,
      "details": "Honors, GPA, etc."
    }
  ],
  "skills": {
    "Technical": ["Python", "JavaScript", "Docker"],
    "Soft Skills": ["Leadership", "Communication"]
  },
  "projects": [...],
  "certifications": [
    {
      "name": "Certification Name",
      "issuer": "Issuing Organization",
      "date": "2023"
    }
  ]
}
```

**Programmatic usage:**
```python
from scripts.generate_docx import ResumeGenerator, StyleConfig

style = StyleConfig(
    accent_color="#2563eb",
    font_family="system",
    font_size="medium",
    spacing="normal"
)

generator = ResumeGenerator(template='minimal', style=style)
generator.generate(resume_data, 'output.docx')
```

## GitHub Integration (Optional)

When a GitHub MCP server is available, offer to pull project data to enrich the
Projects and Skills sections. Read `references/github-integration.md` for the
complete integration workflow.

**Detection:** Check if the user has mentioned GitHub, has repos they want to reference,
or if the conversation context suggests project enrichment would help.

**Graceful fallback:** If no MCP server is available or the user declines, skip this
step entirely. Never require GitHub data — it is purely supplemental.

## Job-Tailoring Algorithm

When tailoring to a job description:

1. **Extract job signals:**
   - Required skills and technologies (from requirements section)
   - Preferred/bonus qualifications
   - Key responsibilities and action verbs
   - Industry-specific terminology
   - Seniority indicators (years of experience, leadership language)

2. **Score resume content:**
   - For each work experience bullet point, calculate keyword overlap with job signals
   - For each skill, check presence in job requirements vs. preferences
   - For each project, assess technology and domain overlap

3. **Reorder by relevance:**
   - Place highest-scoring work experience bullets first within each role
   - Reorder the Skills section: matched required skills → matched preferred → remaining
   - Promote matching projects above non-matching ones
   - If one role is significantly more relevant than others, consider section reordering
     (e.g., moving a highly relevant older role above a less relevant recent one — but
     flag this to the user for approval)

4. **Emphasize alignment:**
   - Generate or update the Professional Summary to reference the target role/company
   - Group skills into categories that mirror the job description's structure
   - Ensure matching certifications are prominently placed

5. **Surface gaps:**
   - Note any required skills the user lacks
   - Suggest the user address these in a cover letter or interview prep

## File Output

Save all generated files to `/mnt/user-data/outputs/`. Use descriptive filenames:
- Baseline: `resume_<name>.<ext>` (e.g., `resume_bob_smith.pdf`)
- Tailored: `resume_<name>_<company>.<ext>` (e.g., `resume_bob_smith_acme.pdf`)

Always present files to the user via the `present_files` tool after generation.

## Error Handling

- If the user provides insufficient information, ask for the minimum: name, one role, and skills
- If a job description is too vague to extract signals, ask for a more complete listing
- If template rendering fails, fall back to the `minimal` template
- If PDF conversion fails, offer HTML output with print-to-PDF instructions
