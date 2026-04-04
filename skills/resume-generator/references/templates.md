# Resume Templates Reference

This file contains the complete HTML/CSS source for each resume template. When generating
HTML or PDF output, select the appropriate template and inject the user's content into
the placeholder structure.

## Template Architecture

All templates share a common structure:
- Single self-contained HTML file with embedded `<style>` block
- CSS custom properties for style configuration (accent color, fonts, spacing)
- `@media print` rules for clean PDF/print output
- `@page` rules for proper page margins and size
- Semantic HTML: `<header>`, `<section>`, `<article>` for accessibility

### Injecting Style Configuration

Replace the CSS custom property defaults in `:root` with the user's style config:

```css
:root {
  --accent: #2563eb;           /* style.accent_color */
  --font-family: system-ui;    /* style.font_family mapping below */
  --font-size: 10pt;           /* style.font_size mapping below */
  --section-gap: 1.2rem;       /* style.spacing mapping below */
  --item-gap: 0.6rem;          /* derived from spacing */
}
```

**Font family mapping:**
- `system` → `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`
- `serif` → `"Georgia", "Times New Roman", serif`
- `sans` → `"Helvetica Neue", "Arial", sans-serif`
- `mono` → `"JetBrains Mono", "Fira Code", "Consolas", monospace`

**Font size mapping:**
- `small` → `9pt` base, headings scale proportionally
- `medium` → `10pt` base
- `large` → `11pt` base

**Spacing mapping:**
- `compact` → `--section-gap: 0.8rem; --item-gap: 0.3rem`
- `normal` → `--section-gap: 1.2rem; --item-gap: 0.6rem`
- `relaxed` → `--section-gap: 1.8rem; --item-gap: 0.9rem`

---

## Template: minimal

Clean single-column layout with generous whitespace. No borders, minimal decoration.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{FULL_NAME}} — Resume</title>
<style>
  :root {
    --accent: {{ACCENT_COLOR|#2563eb}};
    --font-family: {{FONT_FAMILY|system-ui, -apple-system, sans-serif}};
    --font-size: {{FONT_SIZE|10pt}};
    --section-gap: {{SECTION_GAP|1.2rem}};
    --item-gap: {{ITEM_GAP|0.6rem}};
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  @page {
    size: {{PAGE_SIZE|letter}} portrait;
    margin: 0.6in 0.7in;
  }
  body {
    font-family: var(--font-family);
    font-size: var(--font-size);
    line-height: 1.45;
    color: #1a1a1a;
    max-width: 8.5in;
    margin: 0 auto;
    padding: 0.5in;
  }
  @media print {
    body { padding: 0; }
  }
  header { text-align: center; margin-bottom: var(--section-gap); }
  header h1 {
    font-size: 1.8em;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: #111;
    margin-bottom: 0.3rem;
  }
  header .contact {
    font-size: 0.9em;
    color: #555;
  }
  header .contact a { color: var(--accent); text-decoration: none; }
  header .contact span + span::before { content: " · "; color: #aaa; }
  .summary {
    font-style: italic;
    color: #444;
    text-align: center;
    margin-bottom: var(--section-gap);
    max-width: 80%;
    margin-left: auto;
    margin-right: auto;
  }
  section { margin-bottom: var(--section-gap); }
  section h2 {
    font-size: 1.1em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent);
    margin-bottom: 0.5rem;
  }
  .entry { margin-bottom: var(--item-gap); }
  .entry-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
  }
  .entry-header h3 { font-size: 1em; font-weight: 600; color: #222; }
  .entry-header .meta { font-size: 0.9em; color: #666; }
  .entry-header .org { color: #444; font-weight: 400; }
  .entry ul {
    list-style: disc;
    padding-left: 1.4em;
    margin-top: 0.25rem;
  }
  .entry li { margin-bottom: 0.15rem; }
  .skills-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem 1.2rem;
    list-style: none;
    padding: 0;
  }
  .skills-list li { white-space: nowrap; }
  .skills-category { margin-bottom: 0.4rem; }
  .skills-category strong { color: #333; }
</style>
</head>
<body>
  <header>
    <h1>{{FULL_NAME}}</h1>
    <div class="contact">
      <!-- Populate with spans: -->
      <!-- <span>email@example.com</span><span>555-0100</span><span>City, ST</span> -->
      {{CONTACT_LINE}}
    </div>
  </header>

  <!-- Optional summary -->
  <!-- <div class="summary">{{PROFESSIONAL_SUMMARY}}</div> -->

  <!-- Repeat for each section: Experience, Education, Skills, Projects, etc. -->
  <!--
  <section>
    <h2>{{SECTION_TITLE}}</h2>
    <div class="entry">
      <div class="entry-header">
        <h3>{{JOB_TITLE}} <span class="org">— {{COMPANY}}</span></h3>
        <span class="meta">{{DATE_RANGE}}</span>
      </div>
      <ul>
        <li>{{BULLET_POINT}}</li>
      </ul>
    </div>
  </section>
  -->

  {{CONTENT}}
</body>
</html>
```

---

## Template: professional

Structured layout with subtle borders, horizontal rules, and navy accent color.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{FULL_NAME}} — Resume</title>
<style>
  :root {
    --accent: {{ACCENT_COLOR|#1e3a5f}};
    --accent-light: {{ACCENT_LIGHT|#e8eef5}};
    --font-family: {{FONT_FAMILY|"Helvetica Neue", Arial, sans-serif}};
    --font-size: {{FONT_SIZE|10pt}};
    --section-gap: {{SECTION_GAP|1.2rem}};
    --item-gap: {{ITEM_GAP|0.6rem}};
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  @page {
    size: {{PAGE_SIZE|letter}} portrait;
    margin: 0.6in 0.7in;
  }
  body {
    font-family: var(--font-family);
    font-size: var(--font-size);
    line-height: 1.45;
    color: #1a1a1a;
    max-width: 8.5in;
    margin: 0 auto;
    padding: 0.5in;
  }
  @media print { body { padding: 0; } }
  header {
    border-bottom: 2px solid var(--accent);
    padding-bottom: 0.8rem;
    margin-bottom: var(--section-gap);
  }
  header h1 {
    font-size: 1.8em;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0.3rem;
  }
  header .contact {
    font-size: 0.85em;
    color: #555;
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem 1rem;
  }
  header .contact a { color: var(--accent); text-decoration: none; }
  .summary {
    background: var(--accent-light);
    padding: 0.6rem 0.8rem;
    border-left: 3px solid var(--accent);
    margin-bottom: var(--section-gap);
    color: #333;
  }
  section { margin-bottom: var(--section-gap); }
  section h2 {
    font-size: 1.05em;
    font-weight: 700;
    color: var(--accent);
    border-bottom: 1px solid #d0d0d0;
    padding-bottom: 0.25rem;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .entry { margin-bottom: var(--item-gap); }
  .entry-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
  }
  .entry-header h3 { font-size: 1em; font-weight: 600; color: #222; }
  .entry-header .meta { font-size: 0.85em; color: #666; font-style: italic; }
  .entry-header .org { font-weight: 400; color: #444; }
  .entry ul {
    list-style: none;
    padding-left: 1em;
    margin-top: 0.2rem;
  }
  .entry li { margin-bottom: 0.15rem; }
  .entry li::before {
    content: "▸";
    color: var(--accent);
    font-size: 0.8em;
    margin-right: 0.4em;
    margin-left: -1em;
    display: inline-block;
    width: 0.6em;
  }
  .skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.4rem 1.5rem;
  }
  .skills-category strong {
    color: var(--accent);
    font-size: 0.9em;
  }
</style>
</head>
<body>
  <header>
    <h1>{{FULL_NAME}}</h1>
    <div class="contact">{{CONTACT_ITEMS}}</div>
  </header>
  {{CONTENT}}
</body>
</html>
```

---

## Template: modern

Two-column layout with a colored sidebar for contact info and skills.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{FULL_NAME}} — Resume</title>
<style>
  :root {
    --accent: {{ACCENT_COLOR|#6366f1}};
    --accent-dark: {{ACCENT_DARK|#4338ca}};
    --sidebar-bg: {{SIDEBAR_BG|#f1f0ff}};
    --font-family: {{FONT_FAMILY|system-ui, -apple-system, sans-serif}};
    --font-size: {{FONT_SIZE|10pt}};
    --section-gap: {{SECTION_GAP|1.2rem}};
    --item-gap: {{ITEM_GAP|0.6rem}};
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  @page {
    size: {{PAGE_SIZE|letter}} portrait;
    margin: 0.4in;
  }
  body {
    font-family: var(--font-family);
    font-size: var(--font-size);
    line-height: 1.45;
    color: #1a1a1a;
    max-width: 8.5in;
    margin: 0 auto;
  }
  .container {
    display: grid;
    grid-template-columns: 2.2in 1fr;
    min-height: 100vh;
  }
  @media print {
    .container { min-height: auto; }
  }
  .sidebar {
    background: var(--sidebar-bg);
    padding: 1rem 0.8rem;
    border-right: 2px solid var(--accent);
  }
  .sidebar h1 {
    font-size: 1.4em;
    color: var(--accent-dark);
    margin-bottom: 0.2rem;
    line-height: 1.2;
  }
  .sidebar .tagline {
    font-size: 0.85em;
    color: #666;
    margin-bottom: 1rem;
  }
  .sidebar h2 {
    font-size: 0.85em;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent);
    margin-top: 1rem;
    margin-bottom: 0.3rem;
    border-bottom: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
    padding-bottom: 0.15rem;
  }
  .sidebar .contact-item {
    font-size: 0.85em;
    margin-bottom: 0.2rem;
    color: #444;
    word-break: break-word;
  }
  .sidebar .contact-item a { color: var(--accent-dark); text-decoration: none; }
  .sidebar .skill-tag {
    display: inline-block;
    background: white;
    border: 1px solid color-mix(in srgb, var(--accent) 40%, transparent);
    border-radius: 3px;
    padding: 0.1rem 0.4rem;
    font-size: 0.8em;
    margin: 0.1rem 0.1rem;
    color: #333;
  }
  .sidebar .skills-group { margin-bottom: 0.5rem; }
  .sidebar .skills-group-title {
    font-size: 0.8em;
    font-weight: 600;
    color: #555;
    margin-bottom: 0.2rem;
  }
  .main {
    padding: 1rem 1rem 1rem 1.2rem;
  }
  .main section { margin-bottom: var(--section-gap); }
  .main h2 {
    font-size: 1.05em;
    font-weight: 700;
    color: var(--accent-dark);
    margin-bottom: 0.4rem;
    letter-spacing: 0.03em;
  }
  .entry { margin-bottom: var(--item-gap); }
  .entry-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
  }
  .entry-header h3 { font-size: 1em; font-weight: 600; color: #222; }
  .entry-header .meta { font-size: 0.85em; color: #777; }
  .entry-header .org { font-weight: 400; color: #555; }
  .entry ul { list-style: disc; padding-left: 1.3em; margin-top: 0.2rem; }
  .entry li { margin-bottom: 0.12rem; font-size: 0.95em; }
</style>
</head>
<body>
  <div class="container">
    <aside class="sidebar">
      <h1>{{FULL_NAME}}</h1>
      <div class="tagline">{{TAGLINE_OR_TITLE}}</div>
      <h2>Contact</h2>
      {{SIDEBAR_CONTACT}}
      <h2>Skills</h2>
      {{SIDEBAR_SKILLS}}
      <!-- Optional: certifications, languages, etc. in sidebar -->
      {{SIDEBAR_EXTRA}}
    </aside>
    <main class="main">
      {{MAIN_CONTENT}}
    </main>
  </div>
</body>
</html>
```

---

## Template: executive

Traditional, conservative layout with serif fonts and restrained styling.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{FULL_NAME}} — Resume</title>
<style>
  :root {
    --accent: {{ACCENT_COLOR|#333333}};
    --rule-color: #999;
    --font-family: {{FONT_FAMILY|"Georgia", "Times New Roman", serif}};
    --font-size: {{FONT_SIZE|10.5pt}};
    --section-gap: {{SECTION_GAP|1.3rem}};
    --item-gap: {{ITEM_GAP|0.7rem}};
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  @page {
    size: {{PAGE_SIZE|letter}} portrait;
    margin: 0.75in 0.85in;
  }
  body {
    font-family: var(--font-family);
    font-size: var(--font-size);
    line-height: 1.5;
    color: #222;
    max-width: 8.5in;
    margin: 0 auto;
    padding: 0.5in;
  }
  @media print { body { padding: 0; } }
  header {
    text-align: center;
    margin-bottom: 0.5rem;
  }
  header h1 {
    font-size: 1.7em;
    font-weight: 400;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #111;
    margin-bottom: 0.3rem;
  }
  header .contact {
    font-size: 0.85em;
    color: #555;
  }
  header .contact a { color: #333; text-decoration: none; }
  header .contact span + span::before { content: "  |  "; color: #aaa; }
  .divider {
    border: none;
    border-top: 1px solid var(--rule-color);
    margin: 0.6rem 0;
  }
  .summary {
    text-align: center;
    font-style: italic;
    color: #444;
    margin-bottom: 0.3rem;
    padding: 0 2rem;
  }
  section { margin-bottom: var(--section-gap); }
  section h2 {
    font-size: 1em;
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--accent);
    text-align: center;
    margin-bottom: 0.5rem;
  }
  section h2::before, section h2::after {
    content: "———";
    color: var(--rule-color);
    font-size: 0.7em;
    vertical-align: middle;
    margin: 0 0.5em;
  }
  .entry { margin-bottom: var(--item-gap); }
  .entry-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
  }
  .entry-header h3 {
    font-size: 1em;
    font-weight: 700;
    color: #222;
    font-family: var(--font-family);
  }
  .entry-header .meta { font-size: 0.9em; color: #666; }
  .entry-header .org { font-style: italic; font-weight: 400; }
  .entry ul {
    list-style: none;
    padding-left: 1.2em;
    margin-top: 0.2rem;
  }
  .entry li { margin-bottom: 0.15rem; }
  .entry li::before {
    content: "•";
    color: #888;
    margin-right: 0.5em;
    margin-left: -1em;
  }
  .skills-list {
    text-align: center;
    color: #444;
    line-height: 1.6;
  }
</style>
</head>
<body>
  <header>
    <h1>{{FULL_NAME}}</h1>
    <div class="contact">{{CONTACT_LINE}}</div>
  </header>
  <hr class="divider">
  {{CONTENT}}
</body>
</html>
```

---

## Markdown Template

For Markdown output, use this structure:

```markdown
# {{FULL_NAME}}

{{email}} · {{phone}} · {{location}} · {{linkedin}}

---

## Professional Summary

{{SUMMARY_TEXT}}

---

## Experience

### {{JOB_TITLE}} — {{COMPANY}}
*{{START_DATE}} – {{END_DATE}}*

- {{BULLET_1}}
- {{BULLET_2}}

---

## Education

### {{DEGREE}} — {{INSTITUTION}}
*{{GRADUATION_YEAR}}*

{{HONORS_OR_DETAILS}}

---

## Skills

**{{CATEGORY}}:** {{skill1}}, {{skill2}}, {{skill3}}

---

## Projects

### {{PROJECT_NAME}}
{{DESCRIPTION}}
- {{DETAIL_1}}

---

## Certifications

- **{{CERT_NAME}}** — {{ISSUER}}, {{DATE}}
```

Omit any section the user has not provided content for. Do not include empty sections.
