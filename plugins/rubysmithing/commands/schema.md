---
description: Design and implement AI data infrastructure — PostgreSQL/pgvector schemas, chunking pipelines, embedding strategies, neuro-symbolic RAG, SFL metadata schemas, or knowledge graphs. Verifies gem APIs (context-engineer) → designs and implements (agentic-data-engineer) → quality gate (senior-qa-engineer).
argument-hint: "<schema or pipeline description>"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent"]
---

Run the `/rubysmithing:schema` workflow for the data infrastructure described in the arguments.

## Step 1 — Gem Context Verification

Dispatch the `context-engineer` agent with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/schema/step-1-context.md`
- Infrastructure description: from arguments

If Step 1 returns `stdlib-only`, skip to Step 2 directly without gem context.

## Step 2 — Schema Design and Implementation

Dispatch the `agentic-data-engineer` with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/schema/step-2-design.md`
- Infrastructure description: from arguments
- Verified Context Block (or stdlib-only signal): from Step 1

## Step 3 — Quality Gate

Dispatch the `senior-qa-engineer` with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/schema/step-3-verify.md`
- Implementation artifacts: complete output from Step 2

## Final Output

Present:
1. Schema artifacts (Step 2) — migrations, models, pipeline files
2. Verification verdict (Step 3) — SHIP or NEEDS FIXES with specific items
