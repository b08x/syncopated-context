---
description: Translate a foreign codebase (Python, React, Go) to idiomatic Ruby. Deconstructs into a blueprint (rubysmithing-researcher) → verifies gem APIs (rubysmithing-researcher) → implements (rubysmithing-builder).
argument-hint: "<path-to-foreign-codebase-or-paste>"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent"]
---


## Step 1 — Deconstruct

Dispatch the `rubysmithing-researcher` agent with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/translate/step-1-deconstruct.md`
- Target: the foreign codebase path or pasted code from arguments

Wait for all 4 artifacts (Blueprint, Object Graph, Translation Map, Architectural Notes, Gem Requirements).

## Step 2 — Verify Gem APIs

Dispatch the `rubysmithing-researcher` agent with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/translate/step-2-context.md`
- Gem Requirements list: from Step 1

Wait for the complete Verified Context Block before proceeding.

## Step 3 — Implement

Dispatch the `rubysmithing-builder` with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/translate/step-3-implement.md`
- Blueprint: from Step 1
- Verified Context Block: from Step 2

## Final Output

Present:
1. Architectural Notes summary (Step 1 — paradigm gaps and risks)
2. Complete Ruby implementation files (Step 3)
