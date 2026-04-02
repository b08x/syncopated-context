# README Structural Exemplar

This document distills the structural and compositional patterns from a high-quality CLI/OSS README
(the Updo monitoring tool). Use this as the architectural template for all generated READMEs.

---

## Section Order & Purpose

### 1. Header Block
- Centered `<div>` with project name as H1, optional hero image/GIF
- One-sentence tagline describing the tool's core function and value
- Badge row: license, latest release, build status (keep it tight—3-4 badges max)

### 2. Features Section (`## Features`)
- Bulleted list of 5-8 capabilities
- Each bullet: **Bold feature name** — short, benefit-oriented description
- Sequence: lead with the most distinctive/differentiating capabilities
- Avoid implementation details here; save those for dedicated sections

### 3. Demo / Visual Section (`## Demo`)
- Optional but high-value for TUI/CLI tools
- Use `<table>` layout for side-by-side video/GIF comparisons
- Label each demo panel with a short `<h4>` header

### 4. Installation Section (`## Installation`)
- Use `<details>`/`<summary>` collapsible blocks—one per platform/method
- Platform label in summary (e.g., "macOS - Homebrew (Recommended)")
- Lead with the most common/recommended method
- Each block contains only what's needed for that specific path—no cross-contamination

### 5. Usage Section (`## Usage`)
- Open with a concise command synopsis block showing the core invocation patterns
- Follow with a `### Options` subsection organized into named groups (Basic, HTTP, Output, etc.)
- Use short dash-prefixed option lists with concise descriptions
- Close with a `### Examples` subsection—concrete, copy-pasteable commands covering the range of use cases

### 6. Configuration File Section (`## Configuration File`)
- Introduce with a one-sentence context statement (when/why to use a config file vs. CLI flags)
- Provide a minimal but representative TOML/YAML example block
- Follow with a `### Configuration Options` breakdown organized by scope (Global vs. Target)

### 7. Feature Deep-Dives (one section per major feature)
- Each major integration or subsystem gets its own `##` section
- Structure: brief intro → prerequisites or setup → usage examples → troubleshooting note (if needed)
- For integrations (webhooks, Prometheus, AWS): show config examples alongside explanations

### 8. Keyboard Shortcuts (`## Keyboard Shortcuts`)
- Short bulleted list, format: `` `key` ``: Action description
- Only include for interactive TUI tools

### 9. Mentions / Ecosystem (`## Mentions`)
- Short bulleted list of relevant awesome-lists, directories, or ecosystem tools
- Keep brief—signal community recognition without turning into a backlink farm

### 10. Contributing & License
- Short, standard closing blocks
- `## Contributing`: one or two sentences, direct and welcoming
- `## License`: one line with SPDX identifier and link

---

## Compositional Rules

### Badge Selection
Only include badges that carry signal: license, release version, build/quality status.
Avoid vanity badges (downloads, stars) unless they're genuinely informative for the target audience.

### Code Block Discipline
Every command, option flag, config snippet, and JSON payload lives in a fenced code block.
Inline backticks are for short identifiers only (`--flag`, `config.toml`, `target_down`).

### Option Documentation Format
```
- `--flag-name, --alias`: Short description (default: value)
```
Group related flags under a named subheading. Keep descriptions to one line; if it needs more, the flag is complex enough to warrant its own section.

### Callout Blocks
Use `> **Note:**` or `> **📖 Full Documentation:**` sparingly—only when genuinely directing
the reader away from inline detail to avoid overwhelming the current section.

### Table Usage
Reserve `<table>` for visual media layout (side-by-side demos) or structured comparisons
(e.g., AWS permissions tables). Avoid tables for simple key/value data that reads fine as a list.

### Tone Application (per style guide)
- Feature descriptions: low modality, benefit-framed ("can monitor," "supports," "enables")
- Configuration options: factual, neutral, no marketing language
- Prerequisites/warnings: high modality only when technically required ("must configure AWS CLI")
- Examples section: purely instructional, zero prose padding
