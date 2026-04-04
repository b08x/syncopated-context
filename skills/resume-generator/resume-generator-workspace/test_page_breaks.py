#!/usr/bin/env python3
"""
Test script to compare old vs new page break handling.
Uses the actual resume data to generate HTML and test both PDF generators.
"""

import json
import sys
from pathlib import Path

# Add the scripts directory to Python path
scripts_dir = Path(__file__).parent.parent / 'scripts'
sys.path.insert(0, str(scripts_dir))

def markdown_to_json(md_file: Path) -> dict:
    """Convert markdown resume to JSON structure for testing"""
    content = md_file.read_text(encoding='utf-8')

    # Extract basic info
    lines = content.split('\n')

    # Parse name (first line starting with #)
    name = ""
    contact = {}
    summary = ""
    experience = []
    education = []
    skills = {}
    current_section = ""

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Extract name
        if line.startswith('# ') and not name:
            name = line[2:].strip()

        # Extract contact info
        elif '📍' in line or '📧' in line or '📱' in line:
            if '📧' in line:
                # Extract email
                import re
                email_match = re.search(r'📧\s*([^\s|]+)', line)
                if email_match:
                    contact['email'] = email_match.group(1).strip()
            if '📱' in line:
                # Extract phone
                phone_match = re.search(r'📱\s*([^\s|]+(?:\s+[^\s|]+)*)', line)
                if phone_match:
                    contact['phone'] = phone_match.group(1).strip()
            if '📍' in line:
                # Extract location
                loc_match = re.search(r'📍\s*([^|]+)', line)
                if loc_match:
                    contact['location'] = loc_match.group(1).strip()

        # Section headers
        elif line.startswith('## '):
            current_section = line[3:].strip().lower()

        # Professional Summary
        elif current_section == "professional summary" and line and not line.startswith('#'):
            if line != '---':
                summary += line + " "

        # Experience entries
        elif current_section == "professional experience":
            if line.startswith('### '):
                # Job title
                job_title = line[4:].strip()

                # Next line should be company and dates
                if i + 1 < len(lines):
                    i += 1
                    company_line = lines[i].strip()
                    # Parse **Company** | Location format
                    if '**' in company_line and '|' in company_line:
                        company = company_line.split('**')[1].strip()
                        location = company_line.split('|')[1].strip() if '|' in company_line else ""
                    else:
                        company = company_line
                        location = ""

                # Next line should be dates
                if i + 1 < len(lines):
                    i += 1
                    date_line = lines[i].strip()
                    if date_line.startswith('_') and date_line.endswith('_'):
                        dates = date_line[1:-1]  # Remove underscores
                    else:
                        dates = date_line

                # Collect bullet points
                bullets = []
                i += 1
                while i < len(lines):
                    bullet_line = lines[i].strip()
                    if bullet_line.startswith('- '):
                        bullets.append(bullet_line[2:])
                    elif bullet_line.startswith('### ') or bullet_line.startswith('## '):
                        i -= 1  # Back up to process this line again
                        break
                    i += 1

                experience.append({
                    "title": job_title,
                    "company": company,
                    "date_range": dates,
                    "bullets": bullets
                })

        i += 1

    return {
        "name": name,
        "email": contact.get('email', ''),
        "phone": contact.get('phone', ''),
        "location": contact.get('location', ''),
        "linkedin": "",  # Would need more complex parsing
        "summary": summary.strip(),
        "experience": experience,
        "education": education,
        "skills": skills,
        "projects": []
    }

def json_to_html(resume_data: dict, template: str = "minimal") -> str:
    """Convert resume JSON to HTML using minimal template"""

    contact_parts = []
    if resume_data.get('email'):
        contact_parts.append(f'<span>{resume_data["email"]}</span>')
    if resume_data.get('phone'):
        contact_parts.append(f'<span>{resume_data["phone"]}</span>')
    if resume_data.get('location'):
        contact_parts.append(f'<span>{resume_data["location"]}</span>')
    if resume_data.get('linkedin'):
        contact_parts.append(f'<span><a href="https://{resume_data["linkedin"]}">{resume_data["linkedin"]}</a></span>')

    contact_line = ''.join(contact_parts)

    # Build content sections
    content_sections = []

    # Summary section
    if resume_data.get('summary'):
        content_sections.append(f'''
  <div class="summary">{resume_data["summary"]}</div>''')

    # Experience section
    if resume_data.get('experience'):
        exp_entries = []
        for exp in resume_data['experience']:
            bullets_html = '\n'.join([f'        <li>{bullet}</li>' for bullet in exp.get('bullets', [])])
            exp_entries.append(f'''    <div class="entry">
      <div class="entry-header">
        <h3>{exp["title"]} <span class="org">— {exp["company"]}</span></h3>
        <span class="meta">{exp["date_range"]}</span>
      </div>
      <ul>
{bullets_html}
      </ul>
    </div>''')

        exp_section = f'''  <section>
    <h2>Professional Experience</h2>
{chr(10).join(exp_entries)}
  </section>'''
        content_sections.append(exp_section)

    content = '\n'.join(content_sections)

    # Use minimal template
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{resume_data["name"]} — Resume</title>
<style>
  :root {{
    --accent: #2563eb;
    --font-family: system-ui, -apple-system, sans-serif;
    --font-size: 10pt;
    --section-gap: 1.2rem;
    --item-gap: 0.6rem;
  }}
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  @page {{
    size: letter portrait;
    margin: 0.6in 0.7in;
  }}
  body {{
    font-family: var(--font-family);
    font-size: var(--font-size);
    line-height: 1.45;
    color: #1a1a1a;
    max-width: 8.5in;
    margin: 0 auto;
    padding: 0.5in;
  }}
  @media print {{
    body {{ padding: 0; }}
  }}
  header {{ text-align: center; margin-bottom: var(--section-gap); }}
  header h1 {{
    font-size: 1.8em;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: #111;
    margin-bottom: 0.3rem;
  }}
  header .contact {{
    font-size: 0.9em;
    color: #555;
  }}
  header .contact a {{ color: var(--accent); text-decoration: none; }}
  header .contact span + span::before {{ content: " · "; color: #aaa; }}
  .summary {{
    font-style: italic;
    color: #444;
    text-align: center;
    margin-bottom: var(--section-gap);
    max-width: 80%;
    margin-left: auto;
    margin-right: auto;
  }}
  section {{ margin-bottom: var(--section-gap); }}
  section h2 {{
    font-size: 1.1em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent);
    margin-bottom: 0.5rem;
  }}
  .entry {{ margin-bottom: var(--item-gap); }}
  .entry-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
  }}
  .entry-header h3 {{ font-size: 1em; font-weight: 600; color: #222; }}
  .entry-header .meta {{ font-size: 0.9em; color: #666; }}
  .entry-header .org {{ color: #444; font-weight: 400; }}
  .entry ul {{
    list-style: disc;
    padding-left: 1.4em;
    margin-top: 0.25rem;
  }}
  .entry li {{ margin-bottom: 0.15rem; }}
</style>
</head>
<body>
  <header>
    <h1>{resume_data["name"]}</h1>
    <div class="contact">
      {contact_line}
    </div>
  </header>

{content}
</body>
</html>'''

    return html_template


def main():
    """Test page break improvements using real resume data"""
    workspace = Path(__file__).parent

    # Input resume
    resume_md = Path('/home/b08x/Notebook/Resume/Columbus OH Tech Systems Professional.md')

    if not resume_md.exists():
        print(f"Error: Resume file not found: {resume_md}")
        return False

    print("Converting resume to test formats...")

    # Convert markdown to JSON structure
    resume_data = markdown_to_json(resume_md)

    # Generate HTML
    html_content = json_to_html(resume_data)

    # Save HTML file
    html_file = workspace / "test_resume.html"
    html_file.write_text(html_content, encoding='utf-8')
    print(f"Generated HTML: {html_file}")

    # Generate PDFs with both methods
    old_pdf = workspace / "resume_old_pagebreaks.pdf"
    new_pdf = workspace / "resume_new_pagebreaks.pdf"

    # Test old method
    print("\nTesting old page break method...")
    sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
    try:
        from generate_pdf import generate_pdf as old_generate_pdf
        success_old = old_generate_pdf(html_file, old_pdf, add_page_breaks=True)
        if success_old:
            print(f"✓ Old method PDF: {old_pdf}")
        else:
            print("✗ Old method failed")
    except Exception as e:
        print(f"✗ Old method error: {e}")

    # Test new method
    print("\nTesting new dynamic page break method...")
    try:
        from generate_pdf_v2 import generate_pdf as new_generate_pdf
        success_new = new_generate_pdf(html_file, new_pdf, use_dynamic_breaks=True)
        if success_new:
            print(f"✓ New method PDF: {new_pdf}")
        else:
            print("✗ New method failed")
    except Exception as e:
        print(f"✗ New method error: {e}")

    print(f"\nComparison files generated in: {workspace}")
    print("Open both PDFs to compare page break quality:")
    print(f"  Old method: {old_pdf}")
    print(f"  New method: {new_pdf}")

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
