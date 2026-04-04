# ServiceNow KB Article Generator - Skill Overview

## What It Does

Transforms raw technical materials (notes, tickets, screenshots) into professionally formatted ServiceNow Knowledge Base articles following the "Triage-First" troubleshooting methodology.

## When Claude Will Use This Skill

The skill automatically triggers when you:

1. Convert incident resolution notes into KB articles
2. Create structured troubleshooting guides from informal documentation
3. Process screenshots and technical notes into standardized KB format
4. Generate IT support documentation following ServiceNow import standards

## What's Included

### SKILL.md (Main Instructions)

- **Core Workflow**: 4-step process (Analyze → Structure → Format → Validate)
- **Image Reference System**: ID-based screenshot placement
- **Text Formatting Rules**: Bold, monospace, warning styling
- **Quick Template**: Ready-to-use HTML structure
- **Common Patterns**: Hardware, software, and driver troubleshooting examples
- **DOCX Generation**: Automated HTML to DOCX conversion

### scripts/html_to_docx.py (Conversion Script)

Python script that converts KB HTML to ServiceNow-compatible DOCX:

- Proper heading hierarchy (H1-H4)
- Inline image embedding from base64
- Bold and monospace formatting preserved
- Nested lists (bullets and numbered)
- Metadata styling (grey, 10pt)
- Automatic image sizing (max 6.5" width)

**Usage**:

```bash
python3 scripts/html_to_docx.py article.html article.docx
```

**Requirements**: `python-docx`, `Pillow`

### references/template-spec.md (Detailed Specification)

- Complete document hierarchy (H1-H4)
- Metadata formatting
- Image placement rules
- List formatting guidelines
- DOCX export compatibility requirements
- Full working examples

## Key Features

### Triage-First Structure

Automatically organizes content into:

- **Introduction** (🛠️): Purpose, warnings, prerequisites
- **Physical Layer** (🔌): Hardware and connectivity checks
- **OS/Software Layer** (💻): Settings and configuration
- **Advanced Layer** (🚀): Drivers, firmware, escalation

### ServiceNow Compatibility

- Proper HTML hierarchy for clean import
- Inline image placement
- Arial font throughout
- Auto-numbering for lists
- Metadata headers (KB number, version)

### Screenshot Integration

Handles multiple screenshots with ID-based references:

```html
<img src="IMAGE_ID" alt="Description">
```

## Example Usage

**Input**:

```
Notes: "User reported monitor not displaying. Checked power cable - was loose. 
Reconnected and verified LED green. Also updated display settings to Extend mode."
```

**Output**: Structured KB article with:

- Introduction with critical warnings
- Physical checks (power cable verification)
- Software checks (display settings)
- Proper HTML formatting for ServiceNow import

## DOCX Workflow

1. **Generate HTML**: Claude creates the KB article in HTML format
2. **Save to file**: Write HTML to a temporary file (e.g., `article.html`)
3. **Convert to DOCX**: Run the conversion script

   ```bash
   python3 scripts/html_to_docx.py article.html kb_article.docx
   ```

4. **Upload to ServiceNow**: Import the DOCX directly into ServiceNow KB

**Automatic workflow**:

```python
# Claude can do this automatically:
# 1. Generate HTML content
# 2. Save to file
# 3. Run conversion script
# 4. Provide download link
```

The DOCX output is optimized for ServiceNow import with:

- Proper Word styles (Heading 1-3, Normal)
- Inline image placement (not floating)
- Arial font throughout
- Clean HTML-to-Word conversion

## Installation

1. Upload `servicenow-kb-generator.skill` to Claude
2. The skill will automatically be available in your project
3. Claude will use it when you mention KB articles, troubleshooting guides, or ServiceNow documentation

## Tips

- **Provide context**: Mention device/system names, error symptoms
- **Include screenshots**: Label them (error, settings, Device Manager, etc.)
- **Specify KB number**: If you have an existing KB number to update
- **Request variations**: "Make it more technical" or "Simplify for end-users"

## Technical Details

- **Output format**: HTML (ServiceNow-compatible)
- **Export ready**: Structured for DOCX conversion
- **Image handling**: ID-based references (not URLs)
- **Styling**: Minimal, ServiceNow-optimized formatting
