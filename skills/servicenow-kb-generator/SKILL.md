---
name: servicenow-kb-generator
description: Transform raw technical notes and troubleshooting tickets into professionally formatted ServiceNow Knowledge Base articles.
license: MIT
allowed-tools: Read Edit Grep Glob Bash Write
metadata:
  author: b08x
  version: "1.0.0"
  category: automation
---

# ServiceNow KB Article Generator

Transform raw technical materials into structured, ServiceNow-compatible KB articles following the "Triage-First" troubleshooting methodology.

## Core Workflow

### 1. Analyze Input

Identify source material type and extract key information:

- **Incident tickets**: Extract problem, resolution steps, root cause
- **Screenshots**: Identify UI elements, error messages, system state
- **Notes/drafts**: Parse unstructured troubleshooting steps
- **PDFs**: Extract relevant procedures and technical details

### 2. Structure Content

Organize into hierarchical "Triage-First" flow:

```
Introduction (🛠️)
├── Purpose statement
├── Prerequisites/Warnings
└── Critical triage checks

Physical Layer (🔌)
├── Power/connectivity checks
└── Hardware verification

OS/Software Layer (💻)
├── Settings verification
├── Device Manager checks
└── Configuration validation

Advanced Layer (🚀)
├── Driver/firmware updates
└── Advanced diagnostics
```

### 3. Format Output

Generate HTML following ServiceNow import standards:

- Use proper heading hierarchy (H1→H2→H3→H4)
- Bold UI elements and critical warnings
- Insert images inline with ID references
- Apply metadata header (KB number, version)

### 4. Validate Structure

Ensure DOCX export compatibility:

- Images use inline placement
- Lists use proper nesting
- Fonts limited to Arial
- No complex formatting that won't translate

## Image Reference System

**CRITICAL**: When screenshots are provided, use ID-based references:

```html
<img src="IMAGE_ID" alt="Descriptive text">
```

**Rules**:

1. Place images **immediately after** the instruction they illustrate
2. Use the exact ID provided (never invent URLs)
3. Include descriptive alt text
4. Center-align all images

**Example**:

```
Input: [System: Image ID "img-abc123" shows Device Manager]
Output: <img src="img-abc123" alt="Device Manager with Display adapters expanded">
```

## Text Formatting

### Bold (`<strong>`)

Use ONLY for:

- UI elements: **Device Manager**, **Save**, **Display Settings**
- Hardware components: **HDMI IN**, **Power button**
- Critical warnings: **STOP**, **CRITICAL WARNING**
- Expected states: **ON**, **Connected**

### Monospace (`<code>`)

Use for:

- Keyboard shortcuts: `Win + X`, `Ctrl + Alt + Del`
- File paths: `C:\Windows\System32`
- Commands: `ipconfig /all`

### Warnings

```html
<strong>CRITICAL WARNING:</strong> If physical damage, <strong>STOP</strong> and contact Field Service
```

## Quick Template

```html
<!DOCTYPE html>
<html>
<body>
  <h1>[Device/System Name] Troubleshooting</h1>
  <p class="metadata">KB[NUMBER] | v[VERSION]</p>

  <h2>🛠️ Introduction</h2>
  <p>[Purpose statement]</p>
  <ul>
    <li><strong>CRITICAL WARNING:</strong> [Stop conditions]</li>
    <li>[Prerequisites]</li>
  </ul>

  <h2>🔌 Step 1: Physical Checks</h2>
  <h3>1. [Task Name]</h3>
  <ul>
    <li>[Action]</li>
    <li>[Action with UI]: Press <code>Win + X</code> > <strong>Menu Item</strong></li>
  </ul>
  <img src="IMAGE_ID" alt="Description">

  <h2>💻 Step 2: Software Checks</h2>
  [Repeat pattern]

  <h2>🚀 Step 3: Advanced Checks</h2>
  [Escalation procedures]
</body>
</html>
```

## DOCX Generation

After creating the HTML KB article, convert it to DOCX for ServiceNow upload:

```bash
python3 scripts/html_to_docx.py article.html article.docx
```

**The script handles:**

- Proper heading hierarchy (H1-H4)
- Inline image embedding from base64
- Bold and monospace formatting
- Bulleted and numbered lists with nesting
- Metadata styling (grey, 10pt)
- Image sizing (max 6.5" width)

**Workflow:**

1. Generate HTML KB article
2. Save to temporary file: `article.html`
3. Run conversion script
4. Output DOCX ready for ServiceNow import

**Dependencies:**

```bash
pip install python-docx Pillow
```

## Detailed Reference

For complete template specifications, formatting rules, and DOCX export guidelines:

```bash
view references/template-spec.md
```

## Processing Multiple Screenshots

When multiple screenshots are provided:

1. Analyze each for context (error messages, UI state, settings)
2. Create a "Screenshot Analysis" section summarizing findings
3. Reference specific images in relevant troubleshooting steps
4. Use IDs consistently throughout the article

Example flow:

```
User uploads: screenshot1 (error), screenshot2 (Device Manager), screenshot3 (settings)

Output structure:
Introduction → Reference to error shown in screenshot1
Physical Checks → General guidance
Software Checks → Insert screenshot2 with Device Manager steps
            → Insert screenshot3 with settings verification
```

## Best Practices

1. **Progressive complexity**: Start with simple physical checks, advance to technical procedures
2. **Clear triage points**: Include explicit "If X, then STOP and escalate" guidance
3. **Consistent formatting**: Maintain heading hierarchy, bold usage, image placement
4. **Actionable instructions**: Every bullet should be a concrete action
5. **Realistic expectations**: Include approximate time/skill level for each phase

## Common Patterns

### Hardware Troubleshooting

```html
<h2>🔌 Step 1: Physical & Hardware Checks</h2>
<h3>1. Power Verification</h3>
<ul>
  <li>Check power LED status</li>
  <li>Verify cable connections:
    <ul>
      <li>Power cable: Secure at both ends</li>
      <li>Data cable: Firmly seated in <strong>HDMI IN</strong></li>
    </ul>
  </li>
</ul>
```

### Software Configuration

```html
<h2>💻 Step 2: Software & OS Checks</h2>
<h3>1. Display Settings</h3>
<ul>
  <li>Press <code>Win + I</code></li>
  <li>Navigate <strong>System</strong> > <strong>Display</strong></li>
  <li>Verify mode: <strong>Extend</strong> (not Duplicate)</li>
</ul>
```

### Driver/Advanced

```html
<h2>🚀 Step 3: Advanced Checks</h2>
<h3>1. Driver Verification</h3>
<ul>
  <li>Open <strong>Device Manager</strong> (<code>Win + X</code>)</li>
  <li>Check for warning icons</li>
  <li>Update if available</li>
</ul>
```
