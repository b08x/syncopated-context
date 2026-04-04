# Complete Workflow Example

## Scenario

You have troubleshooting notes from an incident ticket that needs to be converted to a KB article.

## Step 1: Input Materials

**Incident Ticket INC0078249**:

```
Problem: User reported JVC diagnostic monitor not displaying in radiology workstation

Resolution:
- Checked power - monitor was off, turned on
- Verified cable in HDMI IN port  
- Cable was loose, reseated firmly
- Checked Windows display settings
- Was set to "Duplicate" mode, changed to "Extend desktop"
- Monitor now working properly

Time to resolve: 15 minutes
```

## Step 2: Generate KB Article (HTML)

**Prompt to Claude**:

```
Create a ServiceNow KB article from this incident resolution. 
Include proper triage structure for future troubleshooting.
```

**Claude generates** (kb_article.html):

```html
<!DOCTYPE html>
<html>
<body>
  <h1>Troubleshooting JVC Diagnostic Monitor - No Display</h1>
  <p class="metadata">KB0010625 | v1.0</p>

  <h2>🛠️ Introduction</h2>
  <p>Structured troubleshooting guide for JVC diagnostic monitors that fail to display output.</p>
  <ul>
    <li><strong>CRITICAL WARNING:</strong> If screen is physically cracked or damaged, <strong>STOP</strong> and contact Field Service.</li>
    <li>Applies to JVC CL-S200 models in radiology workstations</li>
    <li>Estimated time: 10-15 minutes</li>
  </ul>

  <h2>🔌 Step 1: Physical & Hardware Checks</h2>

  <h3>1. Power Verification</h3>
  <ul>
    <li>Check if monitor power button is <strong>ON</strong></li>
    <li>Verify power LED status:
      <ul>
        <li>Green = Normal</li>
        <li>Amber = Standby</li>
        <li>Off = No power</li>
      </ul>
    </li>
    <li>If off, press power button and wait 5 seconds</li>
  </ul>

  <h3>2. Cable Connection</h3>
  <ul>
    <li>Locate <strong>HDMI IN</strong> port on monitor back panel</li>
    <li>Verify cable is fully inserted (should click into place)</li>
    <li>Check cable at computer end as well</li>
    <li>If loose, disconnect and reconnect firmly</li>
  </ul>

  <h2>💻 Step 2: Software & Display Settings</h2>

  <h3>1. Windows Display Configuration</h3>
  <ul>
    <li>Press <code>Win + P</code> to open projection menu</li>
    <li>Verify current mode:
      <ul>
        <li>If set to <strong>Duplicate</strong>, select <strong>Extend</strong></li>
        <li>If set to <strong>PC screen only</strong>, select <strong>Extend</strong></li>
      </ul>
    </li>
    <li>Wait 2-3 seconds for display to activate</li>
  </ul>

  <h3>2. Device Manager Verification</h3>
  <ul>
    <li>Press <code>Win + X</code> and select <strong>Device Manager</strong></li>
    <li>Expand <strong>Display adapters</strong></li>
    <li>Check for yellow warning icons</li>
    <li>If present, right-click and select <strong>Update driver</strong></li>
  </ul>

  <h2>🚀 Step 3: Advanced Troubleshooting</h2>
  <p>If monitor still not displaying after Steps 1-2:</p>
  <ul>
    <li>Test with different HDMI cable</li>
    <li>Try monitor on different workstation to isolate issue</li>
    <li>If problem persists, escalate to Field Service</li>
  </ul>

  <h2>Related Information</h2>
  <p>Reference INC0078249 for similar resolution example.</p>
</body>
</html>
```

## Step 3: Convert to DOCX

**Command**:

```bash
python3 scripts/html_to_docx.py kb_article.html kb_article.docx
```

**Output**:

```
✅ Created: kb_article.docx
```

## Step 4: Verify DOCX Structure

Open `kb_article.docx` in Microsoft Word:

**Heading Structure**:

- Title: "Troubleshooting JVC Diagnostic Monitor - No Display" (Heading 1, 24pt)
- Metadata: "KB0010625 | v1.0" (Normal, 10pt, grey)
- "Introduction" (Heading 1, 18pt)
- "Step 1: Physical & Hardware Checks" (Heading 1, 18pt)
  - "1. Power Verification" (Heading 2, 14pt)
  - "2. Cable Connection" (Heading 2, 14pt)
- "Step 2: Software & Display Settings" (Heading 1, 18pt)
  - "1. Windows Display Configuration" (Heading 2, 14pt)

**Formatting**:

- Bold: UI elements like **HDMI IN**, **Device Manager**, **ON**
- Monospace: Keyboard shortcuts like `Win + P`, `Win + X`
- Bullets: Properly indented with sub-bullets
- Font: Arial throughout
- Images: Would be centered with proper sizing

## Step 5: Upload to ServiceNow

1. Log into ServiceNow
2. Navigate to Knowledge → Create New
3. Click "Import from Word"
4. Upload `kb_article.docx`
5. ServiceNow preserves:
   - Heading hierarchy
   - Formatting (bold, monospace)
   - List structure
   - Image placement
6. Review and publish

## Benefits of This Workflow

**Time Savings**:

- Manual KB creation: 45-60 minutes
- This workflow: 5-10 minutes

**Consistency**:

- Every article follows same structure
- Standardized triage methodology
- Predictable troubleshooting flow

**Quality**:

- Proper ServiceNow formatting
- No manual HTML cleanup needed
- Professional appearance
- Clean DOCX import

## Handling Screenshots

If you have screenshots to include:

**Step 1**: Generate HTML with image placeholders

```html
<img src="img-power-led" alt="Power LED location on JVC monitor">
```

**Step 2**: Before converting to DOCX, replace IDs with base64:

```python
# Replace image IDs with actual base64 data
html_content = html_content.replace(
    'src="img-power-led"',
    'src="data:image/png;base64,iVBORw0KGg..."'
)
```

**Step 3**: Convert to DOCX

```bash
python3 scripts/html_to_docx.py kb_article.html kb_article.docx
```

The script automatically:

- Decodes base64 images
- Embeds them inline
- Sizes them appropriately (max 6.5" width)
- Centers them in the document
