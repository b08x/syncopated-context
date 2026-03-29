---
description: Create a new Ruby app or gem from concept to first implementation. Uses SADD tree-of-thoughts to explore the concept, generates user stories and SDD-compatible backlog, scaffolds the project, and implements the first task with a quality gate.
argument-hint: "<app concept description>"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Agent"]
---

Run the `/rubysmithing:vibe` workflow for the app concept described in the arguments.

## Step 1 — Tree of Thoughts Exploration

Dispatch the `agentic-operations-lead` agent with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/vibe/step-1-tot-explore.md`
- App concept: from arguments

Wait for the complete Project Charter before proceeding.

## Step 2 — User Stories

Dispatch the `agentic-software-engineer` with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/vibe/step-2-user-stories.md`
- Project Charter: from Step 1

## Step 3 — Backlog

Dispatch the `agentic-software-engineer` with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/vibe/step-3-backlog.md`
- User Stories: from Step 2
- Project Charter: from Step 1 (for archetype and complexity)

## Step 4 — Scaffold

Dispatch the `platform-engineer` with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/vibe/step-4-scaffold.md`
- Project Charter: from Step 1

## Step 5 — First Task

Dispatch the `agentic-software-engineer` with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/vibe/step-5-implement.md`
- Scaffolded project: from Step 4
- Backlog: from Step 3

## Final Output

Present:
1. Project Charter (Step 1) — what you're building and why
2. Backlog summary (Step 3) — N tasks, priority breakdown, next steps
3. First task implementation (Step 5) — files created, QA verdict
4. How to continue: `Run /sdd:implement @.specs/tasks/draft/<next-task>.feature.md`
