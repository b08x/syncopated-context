# syncopated-context

Claude Code plugin marketplace distribution featuring **rubysmithing** and **notebook** — convention-aware Ruby development and multi-platform AI session recall. Thirteen specialized Ruby agents handle code generation, TUI scaffolding, AI/NLP integration, refactoring, and QA auditing, while comprehensive recall capabilities aggregate sessions across Claude Code, Hermes, Gemini CLI, and OpenCode with GitHub and backup correlation.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.2.0-green.svg)](.claude-plugin/marketplace.json)
[![Ruby](https://img.shields.io/badge/ruby-3.3.8+-red)](.tool-versions)

---

## Features

- **Adaptive convention detection** — reads `.rubocop.yml`, `standard` in Gemfile, or `.rubysmith` config; falls back to community idioms. Convention target is stated before every generation.
- **Multi-platform session recall** — aggregates AI interactions from Claude Code, Hermes, Gemini CLI, and OpenCode with temporal correlation and cross-platform synthesis.
- **GitHub activity correlation** — correlates session timelines with commit history, PR activity, and code changes using `gh cli` integration.
- **Backup diff analysis** — analyzes restic incremental backups to show file evolution over time, synchronized with session activity.
- **One Thing synthesis** — generates single highest-leverage next action from cross-platform session analysis using momentum detection and blocker identification.
- **Lite / Standard mode switching** — single-file stdlib scripts get lean output; multi-file or gem-touching tasks activate full Standard Mode with Zeitwerk compliance, `frozen_string_literal`, and structured logging.
- **Shared gem API verification** — the `context` agent resolves method signatures via Context7 MCP and caches results in SQLite across sessions before any library-touching code is written.
- **Terminal UI scaffolding** — `tui` generates BubbleTea / Lipgloss / Huh interfaces from a validated skeleton, with keyboard handling and component hierarchy wired up.
- **LLM and RAG pipelines** — `genai` covers chatbots, tool-calling agents, vector search, DSPy reasoning modules, and MCP server scaffolding.
- **SIFT Protocol QA reports** — `sift` runs structured audits against a weighted rubric; findings are filed with `file:line` evidence citations.
- **YARD documentation with type inference** — `yardoc` generates `@param`, `@return`, and `@example` tags for existing Ruby files without requiring manual annotation.
- **Root-cause analysis** — `analyse` traces bugs backward through the call chain using Gemba Walk, Muda waste mapping, and Five Whys before any fix is attempted.

---

## Installation

<details>
<summary>Claude Code — Plugin Marketplace (Recommended)</summary>

Install both plugins together:
```bash
claude plugin add syncopated-context
```

Or install individually:
```bash
claude plugin add syncopated-context/rubysmithing
claude plugin add syncopated-context/notebook
```

After installation, all skills are available in any Claude Code session.

</details>

<details>
<summary>Manual install from source</summary>

```bash
git clone https://github.com/b08x/syncopated-context
cd syncopated-context

# Install both plugins
claude plugin add ./plugins/rubysmithing
claude plugin add ./plugins/notebook

# Or install individually
claude plugin add ./plugins/rubysmithing    # Ruby development suite
claude plugin add ./plugins/notebook       # Multi-platform session recall
```

</details>

<details>
<summary>Ruby toolchain setup (contributors only)</summary>

Requires Ruby 3.3.8 or later via asdf or rbenv (see `.tool-versions`).

```bash
cd plugins/rubysmithing
bundle install
```

</details>

---

## Usage

### Ruby Development (rubysmithing)

Invoke via the `rubysmithing` skill prefix. The `plan` orchestrator routes task types automatically; individual skills can also be invoked directly.

```
rubysmithing:plan           # Hub — routes all Ruby generation tasks
rubysmithing:analyse        # Static analysis: dead code, muda, root-cause tracing
rubysmithing:context        # Gem API verification (Context7 + SQLite cache)
rubysmithing:data-engineer  # Schema design via SADD tree-of-thoughts
rubysmithing:genai          # LLM, RAG, embeddings, DSPy, MCP servers
rubysmithing:refactor       # Convention fixes, Zeitwerk compliance rewrites
rubysmithing:sift           # SIFT Protocol QA audits with weighted rubric
rubysmithing:scaffold       # New project init via rubysmith / gemsmith
rubysmithing:tui            # BubbleTea / Lipgloss / Huh terminal UI
rubysmithing:yardoc         # YARD docs with type inference
```

### Multi-Platform Session Recall (notebook)

The recall skill aggregates sessions across AI platforms with external data correlation:

```bash
# Temporal recall across all platforms
recall yesterday
recall last week across platforms
recall 2025-03-25 with github myrepo

# Platform-specific recall
recall platform:hermes auth work
recall platform:gemini debugging session
recall platform:opencode code review

# Integrated analysis
recall --github owner/repo --backup ~/Workspace authentication refactor
recall this week with backups
```

### Examples

**Ruby Development:**
```
# Generate a PORO with circuit-breaker-wrapped API calls
rubysmithing:plan — build a DataFetcher class that hits the GitHub API

# Design a database schema
rubysmithing:data-engineer — schema for a multi-tenant SaaS with users, orgs, billing

# Build a terminal dashboard
rubysmithing:tui — two-panel TUI: file list left, preview right

# Run a QA audit on the current codebase
rubysmithing:sift — audit lib/
```

**Session Recall:**
```
# Cross-platform work reconstruction
recall authentication work last month

# GitHub correlation
recall --github myrepo/project commits yesterday

# File evolution analysis
recall --backup ~/Workspace schema changes this week

# Multi-source synthesis
recall platform:claude platform:hermes --github myrepo debugging
```

---

## Plugin Architecture

### rubysmithing (Development Suite)

Shared-root pattern with 13 specialized agents:

```
rubysmithing/
├── agents/           — context-engineer, cognitive-architect, ux-engineer, etc.
├── commands/         — workflow commands: context, flow, schema, vibe
├── references/       — gem-registry, cache-cli, genai-patterns, design-patterns
├── scripts/          — context_cache.rb (SQLite gem API cache)
├── tasks/            — SADD task chains: schema design, vibe analysis
├── assets/skeleton/  — TUI project skeleton
└── skills/
    ├── plan/         → orchestrator + error contract + convention references
    ├── analyse/      → Gemba Walk, Muda, Root-Cause Tracing, Five Whys
    ├── data-engineer/ → schema design via SADD tree-of-thoughts
    ├── genai/        → LLM, RAG, embeddings, DSPy, MCP servers
    ├── sift/         → SIFT Protocol QA with weighted rubric
    └── tui/          → BubbleTea / Lipgloss / Huh terminal UI
```

### notebook (Session Recall Suite)

Multi-platform extraction with correlation engines:

```
notebook/
├── skills/recall/
│   ├── scripts/
│   │   ├── multi-platform-extract.py    — unified extraction across platforms
│   │   ├── extract-sessions.py          — Claude Code JSONL parser
│   │   ├── recall-day.py                — temporal session retrieval
│   │   └── session-graph.py             — NetworkX visualization
│   └── workflows/
│       ├── recall.md                    — routing logic and query classification
│       └── multi-platform-recall.md     — correlation process documentation
└── skills/notebooklm/                   — document processing integration
```

---

## Convention Modes

The Ruby development suite selects between two modes before generating any output.

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

## Platform Support

### AI Session Sources

| Platform | Storage Location | Export Method | Format |
|----------|------------------|---------------|--------|
| **Claude Code** | `~/.claude/projects/*/` | Native JSONL parsing | JSONL |
| **Hermes** | SQLite store | `hermes sessions export` | JSONL |
| **Gemini CLI** | `~/.config/gemini/sessions/` | JSON file parsing | JSON |
| **OpenCode** | `~/.config/opencode/logs/` | Log file parsing | Structured logs |

### External Integrations

- **GitHub** — commit correlation, PR activity, and file change analysis via `gh cli`
- **Restic** — backup diff analysis and file evolution tracking
- **NotebookLM** — document processing and artifact import

---

## Roadmap

Additional plugins in development:

- **bashsmithing** — Convention-aware Bash development suite with shellcheck integration, BATS testing, and TUI scaffolding using the Gum/Charm ecosystem
- **fedora-tools** — Fedora packaging, custom ISO building, and system administration workflows
- **linux-audio** — JACK, ALSA, PulseAudio, and PipeWire configuration and troubleshooting workflows

Multi-agent compatibility work is also in progress to adapt command and task structures across Claude Code, Gemini extensions, and other AI coding platforms.

---

## Contributing

Issues and pull requests welcome. Run `bundle exec rubocop` and `bundle exec rspec` from `plugins/rubysmithing/` before submitting; `bundle exec git-lint` validates commit message format.

## License

[MIT](LICENSE) — Robert Pannick