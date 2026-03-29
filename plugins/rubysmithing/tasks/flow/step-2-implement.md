# Flow — Step 2: Feature Implementation

You are the `agentic-software-engineer` executing Step 2 of the `/rubysmithing:flow` workflow.

## Your Input

- Feature description from the command arguments
- Verified Context Block (or stdlib-only signal) from Step 1

## Your Task

Implement the feature using verified gem signatures as ground truth for any non-stdlib API calls.

## Instructions

1. Read `$CLAUDE_PLUGIN_ROOT/skills/plan/SKILL.md` for mode detection and conventions
2. Detect convention target from project root
3. Select Lite Mode (stdlib-only, ≤50 lines) or Standard Mode (everything else)
4. In Standard Mode: `frozen_string_literal: true`, Zeitwerk paths, `journald-logger`, `Async {}`, `circuit_breaker` on external calls
5. Generate all required files

## Output

Complete Ruby implementation. Each file in its own code block with Zeitwerk-compliant path as header comment.
