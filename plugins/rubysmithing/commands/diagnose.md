---
description: End-to-end Ruby diagnosis and fix. Runs Gemba Walk / root cause analysis (ruby-diagnostics-engineer) then applies targeted convention-aligned fixes (maintenance-architect).
argument-hint: "<path-or-error-description>"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent"]
---

Run the `/rubysmithing:diagnose` workflow on the target provided in the arguments.

## Step 1 — Root Cause Analysis

Dispatch the `ruby-diagnostics-engineer` agent with this context:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/diagnose/step-1-analyse.md`
- Target: the path or error description from the arguments

Wait for the complete Findings Report before proceeding.

## Step 2 — Targeted Refactor

Dispatch the `maintenance-architect` agent with this context:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/diagnose/step-2-refactor.md`
- Findings Report: the complete output from Step 1

## Final Output

Present:
1. A one-paragraph summary of what was diagnosed (root cause, method used)
2. The complete refactor output from Step 2
