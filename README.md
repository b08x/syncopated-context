<div align="center">

# rubysmithing

Convention-aware Ruby development suite for Claude Code — orchestrated agents for idiomatic code generation, TUI scaffolding, AI/NLP components, refactoring, QA auditing, and YARD documentation.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](.claude-plugin/marketplace.json)

</div>

---

## Features

- **Adaptive convention detection** — reads `.rubocop.yml`, `standard` in Gemfile, or `.rubysmith` config; falls back to community idioms. Convention target is stated before every generation.
- **Lite / Standard mode switching** — single-file stdlib scripts get lean output; multi-file or gem-touching tasks automatically activate full Standard Mode with Zeitwerk compliance, `frozen_string_literal`, and structured logging.
- **Shared gem API verification** — the `context` agent resolves method signatures via Context7 MCP and caches results in SQLite across sessions before any library-touching code is written.
- **Terminal UI scaffolding** — `tui` generates BubbleTea / Lipgloss / Huh interfaces from a validated skeleton, with keyboard handling and component hierarchy wired up.
- **LLM and RAG pipelines** — `genai` covers chatbots, tool-calling agents, vector search, DSPy reasoning modules, and MCP server scaffolding.
- **SIFT Protocol QA reports** — `sift` runs structured audits against a weighted rubric; findings are filed with `file:line` evidence citations.
- **YARD documentation with type inference** — `yardoc` generates `@param`, `@return`, and `@example` tags for existing Ruby files without requiring manual annotation.
- **Root-cause analysis** — `analyse` traces bugs backward through the call chain using Gemba Walk, Muda waste mapping, and Five Whys before any fix is attempted.

---

## Installation

<details>
<summary>Claude Code — Plugin Marketplace</summary>

```bash
claude plugin install syncopated-context
```

After installation, all skills are available in any Claude Code session.

</details>

<details>
<summary>Manual install from source</summary>

```bash
git clone https://github.com/b08x/syncopated-context
cd syncopated-context
claude plugin install ./plugins/rubysmithing
```

</details>

<details>
<summary>Ruby toolchain setup (contributors only)</summary>

Requires Ruby 3.4.4 via asdf or rbenv (see `.tool-versions`).

```bash
cd plugins/rubysmithing
bundle install
```

</details>

---

## Usage

Invoke via the `rubysmithing` skill prefix in any Claude Code session. The `plan` orchestrator routes task types automatically; individual skills can also be invoked directly.

### Skill entry points

```
rubysmithing:plan      # Hub — routes all Ruby generation tasks
rubysmithing:analyse   # Static analysis: dead code, muda, root-cause tracing
rubysmithing:context   # Gem API verification (Context7 + SQLite cache)
rubysmithing:genai     # LLM, RAG, embeddings, DSPy, MCP servers
rubysmithing:refactor  # Convention fixes, Zeitwerk compliance rewrites
rubysmithing:sift      # SIFT Protocol QA audits with weighted rubric
rubysmithing:scaffold  # New project init via rubysmith / gemsmith
rubysmithing:tui       # BubbleTea / Lipgloss / Huh terminal UI
rubysmithing:yardoc    # YARD docs with type inference
```

### Examples

```
# Generate a PORO with circuit-breaker-wrapped API calls
rubysmithing:plan — build a DataFetcher class that hits the GitHub API

# Scaffold a new gem
rubysmithing:scaffold — create a new gem called my_tool

# Build a terminal dashboard
rubysmithing:tui — two-panel TUI: file list left, preview right

# Generate an LLM chatbot with tool calling
rubysmithing:genai — CLI chatbot using ruby_llm with web search tool

# Run a QA audit on the current codebase
rubysmithing:sift — audit lib/

# Trace a bug before fixing it
rubysmithing:analyse — why is Zeitwerk raising NameError for Foo::Bar?

# Add YARD docs to an existing file
rubysmithing:yardoc — document lib/my_app/processor.rb
```

---

## Convention Modes

The orchestrator selects between two modes before generating any output.

### Lite Mode

Activates for single-file requests under ~50 lines using stdlib only. No `dry-schema`, `async`, or `circuit_breaker`. The `frozen_string_literal` comment is recommended but not enforced. Gem additions are not suggested unless explicitly requested.

### Standard Mode

Default for all other tasks, including any request that produces more than one file. Full conventions apply:

| Convention | Rule |
|---|---|
| Magic comment | `# frozen_string_literal: true` on every file |
| Autoloading | Zeitwerk-compliant path ↔ class name mapping |
| Utility modules | `module_function` not `extend self` |
| Logging | `journald-logger` structured calls, never `puts` |
| I/O concurrency | `Async { }` fiber blocks, not `Thread.new` |
| External API calls | `circuit_breaker` wrapping required |
| Keyword args | Required for methods with 3+ parameters |
| Control flow | Guard clauses over nested conditionals |

Convention target is always detected and stated before generation begins. Detection cascade: `.rubocop.yml` → `standard` in Gemfile → `.rubysmith` config → community idioms.

---

## Skill Architecture

The plugin uses a **shared-root pattern**: agents, references, and scripts used across multiple skills live at the plugin root rather than duplicated inside individual skill directories.

```
rubysmithing (plugin root)
├── agents/           — shared: rubysmithing-context, rubysmithing-genai, rubysmithing-tui
├── references/       — shared: gem-registry, cache-cli, genai-patterns, design-patterns, tui-patterns
├── scripts/          — shared: context_cache.rb (SQLite gem API cache)
├── assets/skeleton/  — shared: TUI project skeleton
└── skills/
    ├── plan/         → orchestrator + error contract + convention references
    ├── analyse/      → Gemba Walk, Muda, Root-Cause Tracing, Five Whys
    ├── context/      → SKILL.md only (agent at root)
    ├── genai/        → SKILL.md only (agent at root)
    ├── refactor/     → convention-targeted rewrites
    ├── scaffold/     → rubysmith / gemsmith project init
    ├── sift/         → SIFT Protocol meta-judge + judge
    ├── tui/          → SKILL.md only (agent + assets at root)
    └── yardoc/       → YARD docs with @param/@return inference
```

Hub-to-spoke delegation uses the Agent tool. Shared resources are referenced via `$CLAUDE_PLUGIN_ROOT/agents/`, `$CLAUDE_PLUGIN_ROOT/references/`, and `$CLAUDE_PLUGIN_ROOT/scripts/` so every skill can access them without path duplication.

---

## Contributing

Issues and pull requests welcome. Run `bundle exec rubocop` and `bundle exec rspec` from `plugins/rubysmithing/` before submitting; `bundle exec git-lint` validates commit message format.

## License

[MIT](LICENSE) — Robert Pannick
