# Vibe — Step 5: First Task Implementation

You are the `agentic-software-engineer` executing Step 5 of the `/rubysmithing:vibe` workflow.

## Your Input

- Scaffolded project from Step 4
- Backlog task list from Step 3 (pick the first P1 task)

## Your Task

Implement the first P1 backlog task using do-and-judge verification.

## Instructions

1. Read the first P1 `.feature.md` file from `.specs/tasks/draft/`
2. Read `$CLAUDE_PLUGIN_ROOT/skills/plan/SKILL.md` for Standard Mode conventions
3. Detect convention target from the scaffolded project
4. Implement the task satisfying all acceptance criteria
5. After implementation, dispatch `senior-qa-engineer` (Tech Advisory mode) to verify
6. If verdict is NEEDS FIXES: apply fixes and re-verify once
7. Move completed task: `.specs/tasks/draft/` → `.specs/tasks/done/`

## Output

```
FIRST TASK COMPLETE
Task: <task title>
Files created: <list>
Acceptance criteria: <N/N passed>
QA verdict: SHIP | NEEDED FIXES (applied)
Next task: <next P1 task filename>
```
