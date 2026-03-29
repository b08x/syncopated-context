<div align="center">

# rubysmithing

Convention-aware Ruby development suite for Claude Code — hub-and-spoke skill system with orchestrated agents for idiomatic code generation, TUI scaffolding, AI/NLP components, refactoring, QA auditing, and YARD documentation.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.2.0-green.svg)](.claude-plugin/marketplace.json)

</div>

---

## Features

- **Adaptive convention detection** — reads `.rubocop.yml`, `standard` in Gemfile, or `.rubysmith` config; falls back to community idioms. Convention target is stated before every generation.
- **Lite / Standard mode switching** — single-file stdlib scripts get lean output; multi-file or gem-touching tasks automatically activate full Standard Mode with Zeitwerk compliance, `frozen_string_literal`, and structured logging.
- **Hub-and-spoke delegation** — one entry point (`rubysmithing`) routes to eight specialized agents based on task type; no manual skill selection required.
- **Gem API verification** — `rubysmithing-context` resolves method signatures via Context7 and caches results in SQLite before any library-touching code is written.
- **Terminal UI scaffolding** — `rubysmithing-tui` generates BubbleTea / Lipgloss / Huh interfaces from a validated skeleton, with keyboard handling and component hierarchy wired up.
- **LLM and RAG pipelines** — `rubysmithing-genai` covers chatbots, tool-calling agents, vector search, DSPy reasoning modules, and MCP server scaffolding.
- **SIFT Protocol QA reports** — `rubysmithing-report` runs structured audits against a weighted rubric; findings are filed with file:line evidence citations.
- **YARD documentation with type inference** — `rubysmithing-yardoc` generates `@param`, `@return`, and `@example` tags for existing Ruby files without requiring manual annotation.

---

## Installation

<details>
<summary>Claude Code — Plugin Marketplace</summary>

```bash
claude plugin install syncopated-context
```

After installation, the `rubysmithing` skill and all sub-agents are available in any Claude Code session.

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

Invoke via the `rubysmithing` skill in any Claude Code session. The orchestrator detects task type and delegates to the appropriate spoke automatically.

### Skill entry points

```
rubysmithing          # Hub — routes all Ruby generation tasks
rubysmithing-analyse  # Static analysis: dead code, muda, root-cause tracing
rubysmithing-context  # Gem API verification (Context7 + SQLite cache)
rubysmithing-genai    # LLM, RAG, embeddings, DSPy, MCP servers
rubysmithing-refactor # Convention fixes, Zeitwerk compliance rewrites
rubysmithing-report   # SIFT Protocol QA audits with weighted rubric
rubysmithing-scaffold # New project init via rubysmith / gemsmith
rubysmithing-tui      # BubbleTea / Lipgloss / Huh terminal UI
rubysmithing-yardoc   # YARD docs with type inference
```

### Examples

```
# Generate a new PORO with circuit-breaker-wrapped API calls
rubysmithing: build a DataFetcher class that hits the GitHub API

# Scaffold a new gem
rubysmithing-scaffold: create a new gem called my_tool

# Build a terminal dashboard
rubysmithing-tui: two-panel TUI — file list on left, preview on right

# Generate an LLM chatbot with tool calling
rubysmithing-genai: CLI chatbot using claude-3-5-sonnet with web search tool

# Run a QA audit on the current codebase
rubysmithing-report: audit lib/

# Add YARD docs to an existing file
rubysmithing-yardoc: document lib/my_app/processor.rb
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

```
rubysmithing (hub / orchestrator)
├── rubysmithing-context   → gem API resolution, SQLite cache
├── rubysmithing-scaffold  → rubysmith / gemsmith project init
├── rubysmithing-genai     → LLM, RAG, DSPy, MCP server code
├── rubysmithing-tui       → BubbleTea, Lipgloss, Huh, Gum, NTCharts
├── rubysmithing-refactor  → convention fixes, Zeitwerk rewrites
├── rubysmithing-report    → SIFT Protocol audits (meta-judge + judge)
├── rubysmithing-yardoc    → YARD docs with @param/@return inference
└── rubysmithing-analyse   → dead code, muda, Zeitwerk NameError tracing
```

Each spoke lives under `plugins/rubysmithing/skills/<name>/` and contains a `SKILL.md` with frontmatter, an `agents/` directory, and a `references/` directory. Hub-to-spoke delegation uses the Agent tool with `$CLAUDE_PLUGIN_ROOT/skills/<name>/` as the path.

---

## Contributing

Issues and pull requests welcome. Run `bundle exec rubocop` and `bundle exec rspec` before submitting; `bundle exec git-lint` validates commit message format.

## License

[MIT](LICENSE) — Robert Pannick
