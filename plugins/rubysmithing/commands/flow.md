---
description: Implement a feature end-to-end. Verifies gem APIs (context-engineer) → implements (agentic-software-engineer) → quality gate (senior-qa-engineer).
argument-hint: "<feature description>"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent"]
---

Run the `/rubysmithing:flow` workflow for the feature described in the arguments.

## Step 1 — Gem Context Verification

Dispatch the `context-engineer` agent with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/flow/step-1-context.md`
- Feature description: from arguments

If Step 1 returns `stdlib-only`, skip to Step 2 directly without gem context.

## Step 2 — Implementation

Dispatch the `agentic-software-engineer` with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/flow/step-2-implement.md`
- Feature description: from arguments
- Verified Context Block (or stdlib-only signal): from Step 1

## Step 3 — Quality Gate

Dispatch the `senior-qa-engineer` with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/flow/step-3-verify.md`
- Implementation files: complete output from Step 2

## Final Output

Present:
1. Implementation files (Step 2)
2. Verification verdict (Step 3) — SHIP or NEEDS FIXES with specific items
