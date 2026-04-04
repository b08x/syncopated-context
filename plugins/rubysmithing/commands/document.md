---
description: Generate comprehensive documentation — YARD API docs (developer-experience-engineer) then wiki pages, guides, and README sections (agentic-software-engineer).
argument-hint: "<path-or-glob>"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent"]
---


## Step 1 — YARD API Documentation

Dispatch the `developer-experience-engineer` agent with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/document/step-1-yardoc.md`
- Target: the file path or glob from arguments

Wait for YARD-annotated files and YARD Coverage Summary before proceeding.

## Step 2 — General Documentation

Dispatch the `agentic-software-engineer` with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/document/step-2-general.md`
- YARD output and Coverage Summary: complete output from Step 1
- Original target: from arguments (for context on what the code does)

## Final Output

Present both documentation artifacts with clear separation between API docs (Step 1) and narrative docs (Step 2).
