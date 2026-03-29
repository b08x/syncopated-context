---
name: rubysmithing-refactor
description: Convention-targeted Ruby refactoring sub-skill. Activates on any mention of: refactor, clean up, fix conventions, this code is messy, help me improve this, anti-patterns, rubocop violations, Zeitwerk compliance, autoload issue, make this idiomatic, extend self, frozen string literal missing, thread usage, hardcoded config, silent rescue, or missing namespace. Accepts pasted code snippets, uploaded files, or filesystem paths. Detects convention target from project config (RuboCop, StandardRB, Rubysmith) before applying changes. Produces pre-refactor audit + complete refactored file + change log. Applies Lite Mode bypass for scripts under ~50 lines where architectural mandates would be disproportionate.
---

# Rubysmithing — Refactor

Targeted refactoring of existing Ruby code toward project-detected conventions.
Always audits before rewriting. Never silently drops functionality.

## Inputs Accepted

- Pasted snippet — inline code in the conversation
- Uploaded file — from `/mnt/user-data/uploads/`
- Filesystem path — via bash tools
- Multiple files — process in dependency order (base classes first)

**Compound prompts** (e.g., "refactor this RAG pipeline AND build a TUI for it"):
Handle the refactoring component here. State:
"Handling refactor. TUI scaffolding should be addressed with rubysmithing-tui."

## Step 1: Detect Convention Target

Priority order:

1. `.rubocop.yml` → RuboCop (parse enabled cops, target Ruby version)
2. `standard` in Gemfile → StandardRB
3. `.rubysmith` / `rubysmith` gem → Rubysmith defaults
4. None → community idioms from `references/refactor-patterns.md`

## Step 2: Detect Mode

### Lite Mode

Apply when: file is ≤ ~50 lines, or request is clearly a simple utility script.

Lite Mode refactor scope:

- Style fixes only (frozen string literal, indent, naming, guard clauses)
- Do NOT add async, circuit breakers, or dry-schema
- Do NOT mandate journald-logger for a one-off script
- Note: "Lite Mode applied — architectural mandates omitted (disproportionate for scope)"

### Standard Mode

Apply for all other inputs. Full pattern catalog from `references/refactor-patterns.md`.

## Step 3: Pre-Refactor Audit

Before rewriting, output a brief audit:

```
FILE: lib/my_app/processor.rb
Convention target: RuboCop (.rubocop.yml detected)
Mode: Standard

CRITICAL
  [line 3]  Thread.new usage — use Async fiber            [thread_to_async]
  [line 1]  No frozen_string_literal                      [missing_frozen_string_literal]
WARNING
  [line 8]  extend self — use module_function             [extend_self_to_module_function]
  [line 22] Nested conditionals depth 3 — guard clauses  [nested_conditionals]
INFO
  [line 1]  No namespace wrapper                          [missing_namespace]
```

Pattern names in brackets map to `references/refactor-patterns.md`.

## Step 4: Refactor

Apply changes. For each non-trivial transformation:

- Show before/after inline for any change that alters behavior
- Add inline comment if refactored pattern is non-obvious
- Flag explicitly if a change alters observable behavior

## Step 5: Verify Zeitwerk Compliance

Confirm post-refactor:

- Module/class name matches file path exactly
- No `require` for Zeitwerk-managed files
- `loader.collapse` / `loader.push_dir` used correctly for non-standard paths

## Output Format

1. Pre-refactor audit (issues, severity, pattern key)
2. Complete refactored file — always full file, never diff-only
3. Change log — bullet list of what changed and why
4. Behavioral changes — flagged explicitly if any
5. Mode applied — Lite or Standard + convention target
