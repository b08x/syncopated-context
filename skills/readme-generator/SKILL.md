---
name: readme-generator
description: This skill should be used whenever a user wants to generate, rewrite, or significantly improve a README.md for a software project. Triggers include requests like "write a README for my project," "generate documentation for this tool," "make a README from this codebase," or providing a project description/codebase and asking for documentation. The output follows a specific structural exemplar (CLI/OSS style) and an opinionated Technical Research Style Guide governing tone, prose rhythm, and formatting discipline. This skill should NOT be used for generating inline API docs, docstrings, changelogs, or contributing guides as standalone deliverables.
---

# README Generator Skill

Generate production-quality README.md files following a proven structural template and an
opinionated style guide. The output targets developer-facing OSS and CLI projects—though the
structural and tonal conventions adapt well to any technical tool.

## Workflow

### Step 1: Gather Project Context

Before writing, load both reference files:

- `references/readme-structure.md` — structural template and compositional rules
- `references/style-guide.md` — tone, prose rhythm, punctuation, and depth guidelines

Then collect the following from the user's input (extract from provided code, description, or
conversation; ask only for what's genuinely missing):

**Required:**
- Project name and one-sentence purpose
- Primary language / runtime
- Core features (at least 3-5)
- Installation method(s)
- Basic usage / primary command syntax

**Optional but high-value:**
- Configuration options (CLI flags, config file format)
- Integration points (webhooks, APIs, external services)
- Demo assets (GIFs, screenshots, video URLs)
- License type
- Contribution stance

If the user provides source code or a repo dump, extract this context programmatically rather
than asking for it.

### Step 2: Map to Structure

Using `references/readme-structure.md`, determine which sections apply to this project:

- All projects: Header Block, Features, Installation, Usage, Contributing, License
- CLI/TUI tools: add Demo, Keyboard Shortcuts
- Config-driven tools: add Configuration File section
- Integration-heavy tools: add per-feature deep-dive sections
- Multi-platform tools: use `<details>` collapsibles in Installation

Omit sections that don't apply rather than padding them with placeholder content.

### Step 3: Draft the README

Apply the style guide throughout. Key enforcement points:

**Prose:**
- Detached authority voice—no "I" or "we"; frame as systemic observations
- Low modality by default; reserve "must/requires" for hard technical constraints
- Paragraphs capped at 4-5 lines; transition to lists only for enumerable steps or options
- Inject dry, domain-adjacent humor sparingly in dense sections

**Structure:**
- Every command, flag, config snippet, and JSON payload in a fenced code block
- Inline backticks for short identifiers only
- Option docs format: `- \`--flag\`: Description (default: value)`
- `> **Note:**` callouts used sparingly and only when genuinely warranted

**Depth:**
- Features section: benefit-framed, no implementation details
- Configuration: 60% current actionable state, 40% context for *why* it's structured that way
- Avoid theoretical deep-dives unless the underlying mechanic directly affects user behavior

### Step 4: Deliver

Output the complete README as a raw Markdown file delivered via `present_files`.

If the user asks for revisions, apply targeted edits rather than regenerating the full document—
preserve sections that weren't in scope for the change.

## Common Failure Modes to Avoid

- **Feature-dumping in the header:** The tagline and badge row carry the hook; save feature
  details for the Features section.
- **Flat Installation sections:** Use `<details>` collapsibles for multi-platform installs.
  A wall of platform-specific commands in one block destroys scannability.
- **Options without grouping:** Ungrouped flag lists become unnavigable past ~8 flags. Always
  organize into named groups (Basic, HTTP, Output, etc.).
- **Marketing language in config docs:** Configuration option descriptions are factual, not
  persuasive. "Enables powerful real-time webhook alerting" -> "Webhook URL for up/down notifications."
- **Missing examples section:** A Usage section without concrete, copy-pasteable examples is
  incomplete. Examples carry more instructional load than prose descriptions.
