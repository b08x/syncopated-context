# Translate — Step 3: Ruby Implementation

You are the `agentic-software-engineer` executing Step 3 of the `/rubysmithing:translate` workflow.

## Your Input

You receive:
- Blueprint (module/class structure from Step 1)
- Verified Context Block for each gem (from Step 2)

## Your Task

Implement the Ruby code from the Blueprint using only the verified gem signatures from Step 2 as ground truth for non-stdlib library calls.

## Instructions

1. Read `$CLAUDE_PLUGIN_ROOT/skills/plan/SKILL.md` for Standard Mode conventions
2. Detect convention target from project root
3. Apply Standard Mode (this is a multi-file translation — always Standard, never Lite)
4. Use only the method signatures from the Verified Context Block — do not invent API calls
5. Apply: `frozen_string_literal: true`, Zeitwerk-compliant paths, `journald-logger` not `puts`, `Async {}` not `Thread.new`, `circuit_breaker` on external calls

## Output

Complete, runnable Ruby implementation files. Each file on its own code block with its Zeitwerk-compliant path as a header comment.
