# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a Claude Code plugin marketplace repository. It packages the **rubysmithing** plugin — a convention-aware Ruby development suite — for distribution via the Claude Code plugin system.

The marketplace manifest is at `.claude-plugin/marketplace.json`. The plugin itself lives under `plugins/rubysmithing/`.

## Plugin Structure

```
plugins/rubysmithing/
├── .claude-plugin/plugin.json   # Plugin metadata and version
├── skills/                      # 9 skill definitions (hub-and-spoke)
│   ├── rubysmithing/            # Hub/orchestrator — routes to spokes
│   ├── rubysmithing-analyse/    # Code analysis and findings
│   ├── rubysmithing-context/    # Gem API verification via Context7 + SQLite cache
│   ├── rubysmithing-genai/      # LLM, RAG, DSPy, MCP server scaffolding
│   ├── rubysmithing-refactor/   # Convention-targeted rewriting
│   ├── rubysmithing-report/     # SIFT Protocol QA audits
│   ├── rubysmithing-scaffold/   # rubysmith/gemsmith project initialization
│   ├── rubysmithing-tui/        # BubbleTea/Lipgloss/Huh terminal UI
│   └── rubysmithing-yardoc/     # YARD documentation generation
├── Gemfile                      # Ruby dependencies for plugin toolchain
└── .rubocop.yml                 # RuboCop config (Ruby 3.4, extensive rule set)
```

Each skill directory contains: `SKILL.md` (frontmatter + instructions), `agents/`, `commands/`, `references/`, and optionally `scripts/` or `assets/`.

## Ruby Toolchain

Ruby version: **3.4.4** (`.tool-versions` / `.ruby-version`)

All commands run from `plugins/rubysmithing/`:

```bash
# Install dependencies
bundle install

# Lint
bundle exec rubocop

# Lint with autocorrect
bundle exec rubocop -a

# Tests
bundle exec rspec

# Single spec file
bundle exec rspec spec/path/to/file_spec.rb

# Git commit quality
bundle exec git-lint
```

## Skill Authoring Conventions

Skill frontmatter supports only `name` (≤64 chars) and `description` (≤1024 chars, third person). Do not add other frontmatter fields.

### Hub-and-Spoke Delegation

`rubysmithing` is the hub. It delegates to spokes via the Agent tool using paths like `$CLAUDE_PLUGIN_ROOT/skills/rubysmithing-context/`. Never flatten this routing — the hub detects mode (Lite vs Standard) and convention target before delegating.

### Lite Mode vs Standard Mode

- **Lite Mode**: single-file ≤~50 lines, stdlib only — no `dry-schema`, `async`, `circuit_breaker`, no `frozen_string_literal` mandate
- **Standard Mode**: all other tasks — full conventions, `frozen_string_literal: true` on every file, Zeitwerk-compliant paths, `journald-logger` not `puts`, `Async {}` not `Thread.new`, `circuit_breaker` on external calls

### SKILL.md Size

Keep each SKILL.md under 500 lines. Move detailed reference material to `references/*.md` and link from SKILL.md. All reference links must be one level deep — no `references/sub/file.md`.
