# ServiceNow KB Article Template Specification

This specification defines the exact structure for KB articles optimized for ServiceNow import via the Notes + Screenshots → .docx → ServiceNow KB pipeline.

## Document Hierarchy

### Level 1: Document Title
- **HTML**: `<h1>`
- **Purpose**: Article title
- **Style**: 24pt, Bold, Arial
- **Example**: `<h1>Troubleshooting JVC Diagnostic Monitor</h1>`

### Level 2: Major Phases
- **HTML**: `<h2>`
- **Purpose**: Primary sections (Introduction, Step blocks)
- **Style**: 18pt, Bold, Arial
- **Icons**: 🛠️ (Introduction), 🔌 (Hardware), 💻 (Software), 🚀 (Advanced)
- **Example**: `<h2>🔌 Step 1: Physical & Hardware Checks</h2>`

### Level 3: Sequential Steps
- **HTML**: `<h3>`
- **Purpose**: Individual troubleshooting tasks
- **Style**: 14pt, Bold, Arial
- **Numbering**: "1. Task Name", "2. Task Name"
- **Example**: `<h3>1. Power On Verification</h3>`

### Level 4: Sub-Tasks
- **HTML**: `<h4>` or `<strong>` within list
- **Purpose**: Detailed sub-procedures
- **Style**: 12pt, Bold, Arial

### Level 5: Action Items
- **HTML**: `<ul>` (bullets) or `<ol>` (numbered)
- **Purpose**: Specific instructions
- **Nesting**: Support 2 levels for conditional logic

## Metadata Header

Place immediately after title:
```html
<p class="metadata">KB[NUMBER] | v[VERSION]</p>
```

Style: 10pt, Grey (#666666), Arial

## Text Formatting Rules

### Bold (`<strong>`)
Use **ONLY** for:
- UI elements: **Device Manager**, **Save**, **Extend desktop**
- Port/button names: **HDMI IN**, **Power ON**
- Critical warnings: **STOP**, **CRITICAL WARNING**
- Expected outcomes: **ON**, **Connected**

### Monospace (`<code>`)
Use for:
- Keyboard shortcuts: `Win + X`, `Ctrl + Alt + Del`
- File paths: `C:\Windows\System32`
- Commands: `ipconfig /all`

### Warning Text
```html
<span class="warning">CRITICAL: Contact Field Service immediately</span>
```
Style: Red (#FF0000), Bold

## Image Placement

### Reference System
Images must use ID-based references:
```html
<img src="IMAGE_ID" alt="Description of screenshot">
```

### Placement Rules
1. Place **immediately after** the instruction it depicts
2. **Center-align** all images
3. Include descriptive alt text
4. Size: Max width 650px (auto-scaled in DOCX)

### Example
```html
<h3>1. Check Display Settings</h3>
<ul>
  <li>Right-click Desktop</li>
  <li>Select <strong>Display Settings</strong></li>
</ul>
<img src="img-abc123" alt="Screenshot showing Display Settings menu highlighted">
```

## Introduction Section Structure

Required components:
1. **Purpose statement** (single paragraph)
2. **Scope/Prerequisites** (bullet list)
3. **Critical Triage Checks** (bulleted warnings)

Example:
```html
<h2>🛠️ Introduction</h2>
<p>To provide structured troubleshooting for JVC diagnostic monitors with power/signal issues.</p>
<ul>
  <li><strong>CRITICAL WARNING:</strong> If physical damage observed, <strong>STOP</strong> and contact Field Service.</li>
  <li>Applies to JVC CL-S200 models only</li>
  <li>Requires Windows 10/11 with admin access</li>
</ul>
```

## Troubleshooting Flow Pattern

Use "Triage-First" progression:

1. **Physical Layer** (🔌)
   - Power checks
   - Cable connections
   - Physical damage assessment

2. **OS/Software Layer** (💻)
   - Settings verification
   - Device Manager checks
   - Display configuration

3. **Advanced/Driver Layer** (🚀)
   - Driver updates
   - Advanced settings
   - Firmware checks

## List Formatting

### Unordered Lists
```html
<ul>
  <li>First action</li>
  <li>Second action</li>
  <li>Conditional check:
    <ul>
      <li>If yes: proceed</li>
      <li>If no: stop</li>
    </ul>
  </li>
</ul>
```

### Ordered Lists
Use for sequential procedures where order matters:
```html
<ol>
  <li>Power on device</li>
  <li>Wait 30 seconds</li>
  <li>Check LED status</li>
</ol>
```

## DOCX Export Compatibility

### Required Practices
1. **Images**: Use inline placement (`In Line with Text`)
2. **Lists**: Use auto-numbering (never manual "1.")
3. **Tables**: Avoid complex tables; use simple 2-column layouts only
4. **Fonts**: Stick to Arial throughout
5. **Colors**: Limit to black text, red warnings, grey metadata

### Avoid
- Floating images
- Manual numbering
- Mixed fonts
- Complex CSS that won't translate
- Background images or gradients

## Complete Example

```html
<!DOCTYPE html>
<html>
<body>
  <h1>Troubleshooting JVC Diagnostic Monitor</h1>
  <p class="metadata">KB0010624 | v3.0</p>

  <h2>🛠️ Introduction</h2>
  <p>Structured guide for JVC diagnostic monitors exhibiting power or signal issues.</p>
  <ul>
    <li><strong>CRITICAL WARNING:</strong> If physical damage observed, <strong>STOP</strong> and contact Field Service.</li>
    <li>Applies to JVC CL-S200 models</li>
  </ul>

  <h2>🔌 Step 1: Physical & Hardware Checks</h2>

  <h3>1. Power On Verification</h3>
  <ul>
    <li>Ensure monitor powers on</li>
    <li>Verify toggle button is <strong>ON</strong></li>
    <li>Check power LED status:
      <ul>
        <li>Green = Normal</li>
        <li>Amber = Standby</li>
        <li>Off = No power</li>
      </ul>
    </li>
  </ul>
  <img src="img-power-button" alt="Power button location with ON indicator">

  <h3>2. Cable Connection</h3>
  <ul>
    <li>Confirm cable in <strong>HDMI IN</strong> port</li>
    <li>Verify cable firmly seated</li>
  </ul>
  <img src="img-hdmi-port" alt="HDMI IN port highlighted in yellow">

  <h2>💻 Step 2: Software & OS Checks</h2>

  <h3>1. Display Settings</h3>
  <ul>
    <li>Press <code>Win + I</code> to open Settings</li>
    <li>Navigate to <strong>System</strong> > <strong>Display</strong></li>
    <li>Verify <strong>Extend desktop to this display</strong> is selected</li>
  </ul>
  <img src="img-display-settings" alt="Display settings with Extend option selected">

  <h2>🚀 Step 3: Advanced Checks</h2>
  <p>If issues persist after basic troubleshooting, escalate to Field Service.</p>
</body>
</html>
```
