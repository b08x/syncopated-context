---
name: plan
description: Convention-aware Ruby code generator for the terminal-native AI orchestration stack (dotenv, tty-config, zeitwerk, async, dry-schema, sequel, journald-logger, circuit_breaker, parallel, concurrent-ruby). Use for generating Ruby classes, modules, Rake tasks, config wiring, boot layer code, data pipelines, POROs, error class hierarchies, parallel processing workers, content parsers, and Gemfile decisions. Applies project-detected conventions (RuboCop, StandardRB, or community idioms) automatically. For single-file output under ~50 lines or pure stdlib work, activates Lite Mode — no dry-schema, no async, no circuit breakers. Multi-file scaffold requests always use Standard Mode regardless of per-file line count. Does NOT handle: LLM/AI/NLP code (genai), TUI interfaces (tui), refactoring (refactor), quality reports (sift), or YARD documentation (yardoc). Always defers to rubysmithing-researcher for gem API verification before generating library-specific code.
---

# Rubysmithing

Convention-aware Ruby code generator. Generates complete, idiomatic Ruby files
calibrated to project-detected conventions and task scope.

## Agent Delegation Pattern

This skill dispatches to specialized sub-agents via the **Rubysmithing Sovereign** orchestrator.

| Task Type | Sub-Agent | Role |
|:----------|:----------|:-----|
| **Generation** | `rubysmithing-builder` | Scaffolding, AI/NLP, TUI, Data, DX, General Code |
| **Research** | `rubysmithing-researcher` | Gem API verification, Codebase Survey, Foreign Translation |
| **Quality/Repair** | `rubysmithing-auditor` | SIFT Audits, Diagnostics, Refactoring, Evaluation |

**Delegation pattern**: Use the Task tool to invoke the required sub-agent from `$CLAUDE_PLUGIN_ROOT/agents/`. Complex workflows (diagnose+fix, audit+score, etc.) are orchestrated by the Sovereign using these three agents in sequence or parallel.

## Step 1: Detect Mode

### Lite Mode (single-file output ≤ ~50 lines, or explicitly simple tasks)

Triggers: "quick script", "simple utility", "one-off", "no dependencies", "stdlib only",
or a clearly small self-contained task.

**Multi-file scaffold requests always trigger Standard Mode** regardless of individual
file line count. If the task would produce more than one file, apply Standard Mode.

For **new project initialization** (rubysmith or gemsmith scaffold): delegate to
`rubysmithing-builder`. This skill handles code within an existing project;
the builder handles the project skeleton itself.

In Lite Mode:

- Generate pure Ruby using stdlib only
- No `dry-schema`, no `dry-types`, no `async`, no `circuit_breaker`
- No `frozen_string_literal` mandate (still recommended, but not enforced)
- Output a single file with a brief inline comment explaining any non-obvious choice
- Do not suggest adding gems unless the user asks

### Standard Mode (default for all other tasks)

Apply full conventions from `references/conventions.md`.

## Step 2: Detect Convention Target

See `references/convention-detection.md` for the canonical detection cascade and
reporting format. Summary:

1. `.rubocop.yml` present → use RuboCop config
2. `standard` in Gemfile → use StandardRB
3. `.rubysmith` / `rubysmith` gem → use Rubysmith defaults
4. None → apply community idioms from `references/conventions.md`

Always state which target was detected and from which artifact before generating.

## Step 3: Gem Context Check

Before writing any code that touches a gem:

- Note which gems are involved
- State: "Deferring to rubysmithing-researcher for [gem] API verification"
- In practice, if rubysmithing-researcher is active in the session and has already
  resolved the gem, use the cached result directly

Skip this step for: stdlib only, Lite Mode tasks, gems already resolved this session.

## Step 4: Generate

Generate complete files. No truncation. No `# ... rest of implementation` stubs.

### Standard Mode conventions — always apply

```ruby
# frozen_string_literal: true          # first line of every file
```

- Two-space indent, no tabs
- `snake_case` methods/vars, `CamelCase` classes/modules, `SCREAMING_SNAKE` constants
- `Struct.new(keyword_init: true)` for value objects
- Keyword args for 3+ param methods
- Guard clauses over nested conditionals
- Zeitwerk-compliant path ↔ class name
- `module_function` not `extend self`
- `journald-logger` not `puts`
- `Async { }` not `Thread.new` for I/O
- `circuit_breaker` wrapping external API calls

## Output Format

1. **File path** — relative to project root
2. **Complete file content**
3. **Rationale** — one sentence for non-obvious decisions only
4. **Gemfile additions** — if new gems required
5. **Mode applied** — "Lite Mode" or "Standard Mode [convention target]"
