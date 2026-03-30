---
name: add-or-update-workflow-command
description: Workflow command scaffold for add-or-update-workflow-command in syncopated-context.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-or-update-workflow-command

Use this workflow when working on **add-or-update-workflow-command** in `syncopated-context`.

## Goal

Adds a new workflow command (e.g., /rubysmithing:flow, /rubysmithing:vibe, /rubysmithing:diagnose) and its associated multi-step task chain for the rubysmithing plugin.

## Common Files

- `plugins/rubysmithing/commands/<workflow>.md`
- `plugins/rubysmithing/tasks/<workflow>/step-*.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create or update a command file in plugins/rubysmithing/commands/ (e.g., flow.md, vibe.md, audit.md, diagnose.md, document.md, translate.md)
- Create a set of task step files in plugins/rubysmithing/tasks/<workflow>/ (e.g., step-1-*.md, step-2-*.md, step-3-*.md, etc.)
- Optionally update or create related agent or SKILL.md files if the workflow is agent-driven

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.