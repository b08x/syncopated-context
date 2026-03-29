# Vibe — Step 3: Prioritized Backlog

You are the `agentic-software-engineer` executing Step 3 of the `/rubysmithing:vibe` workflow.

## Your Input

User stories from Step 2 and Project Charter from Step 1.

## Your Task

Decompose stories into prioritized backlog tasks in SDD-compatible format. Each task is independently implementable and produces verifiable output.

## Output Format

Create files at `.specs/tasks/draft/<N>-<slug>.feature.md` for each task. Use this template for each:

```markdown
# <Task Title>

## Story
As a <role>, I want <action> so that <outcome>.

## Acceptance Criteria
- [ ] <specific, testable criterion>
- [ ] <specific, testable criterion>
- [ ] <specific, testable criterion>

## Technical Notes
<implementation hints — gem to use, Standard Mode requirement, Zeitwerk path>

## Dependencies
<task numbers this depends on, or "none">

## Priority
P1 (must-have) | P2 (should-have) | P3 (nice-to-have)
```

## Ordering Rules
- P1 tasks first, ordered by dependency chain
- Infrastructure/boot layer before feature code
- Independent tasks at the same priority level may be parallelized

## Output

List all task files created with their priorities and dependency chain. End with:
```
BACKLOG READY: N tasks created in .specs/tasks/draft/
SDD-compatible: yes — run /sdd:implement @.specs/tasks/draft/<first-task>.feature.md to begin
```
