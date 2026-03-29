# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a Claude Code plugin marketplace repository. It packages the **rubysmithing** plugin — a convention-aware Ruby development suite — for distribution via the Claude Code plugin system.

The marketplace manifest is at `.claude-plugin/marketplace.json`. The plugin itself lives under `plugins/rubysmithing/`.

## Plugin Structure

The plugin uses a **shared-root architecture** modeled after the sdd plugin pattern. Agents, references, and scripts used by multiple skills live at the plugin root rather than inside individual skill directories.

```
plugins/rubysmithing/
├── .claude-plugin/plugin.json   # Plugin metadata and version (v2.0.0)
├── agents/                      # Shared agents (context, genai, tui)
├── commands/                    # Shared commands (context)
├── references/                  # Shared references (gem-registry, cache-cli, genai-patterns, design-patterns, tui-patterns)
├── scripts/                     # Shared scripts (context_cache.rb — SQLite gem cache)
├── assets/skeleton/             # TUI project skeleton (copied and renamed per scaffold)
├── skills/
│   ├── plan/        # Hub/orchestrator — routes to spokes; holds error-contract.md, conventions.md
│   ├── analyse/     # Gemba Walk, Muda, Root-Cause Tracing, Five Whys
│   ├── context/     # SKILL.md only — agent/commands/refs/scripts live at plugin root
│   ├── genai/       # SKILL.md only — agent/refs at plugin root
│   ├── refactor/    # Convention-targeted rewriting
│   ├── scaffold/    # rubysmith/gemsmith project initialization
│   ├── sift/        # SIFT Protocol V1.0 QA audits
│   ├── tui/         # SKILL.md only — agent/refs/assets at plugin root
│   └── yardoc/      # YARD documentation generation
├── Gemfile                      # Ruby dependencies for plugin toolchain
└── .rubocop.yml                 # RuboCop config (Ruby 3.4, extensive rule set)
```

Skills that are purely SKILL.md (context, genai, tui) have had their agents/references/assets elevated to plugin root so all skills can reference them via `$CLAUDE_PLUGIN_ROOT/agents/`, `$CLAUDE_PLUGIN_ROOT/references/`, etc.

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

### Shared vs Skill-Local Resources

- **Shared** (at plugin root): resources used by multiple skills — the context agent, gem-registry, cache-cli, genai-patterns, design-patterns, tui-patterns, context_cache.rb, assets/skeleton/
- **Skill-local**: resources used only within a single skill — keep them in `skills/<name>/references/`, `skills/<name>/agents/`, etc.

When a skill references a shared resource, use the full path: `$CLAUDE_PLUGIN_ROOT/references/gem-registry.md` (not a relative path). When referencing a skill-local resource from within that skill's SKILL.md, relative paths (`references/foo.md`) work.

### Delegation from plan

The `plan` skill (hub) delegates to spokes via the Agent tool. Spoke agents are discovered at `$CLAUDE_PLUGIN_ROOT/agents/` (for shared agents) or `$CLAUDE_PLUGIN_ROOT/skills/<name>/agents/` (for skill-local agents). The orchestrator in `skills/plan/agents/` detects mode (Lite vs Standard) and convention target before delegating.

### Lite Mode vs Standard Mode

- **Lite Mode**: single-file ≤~50 lines, stdlib only — no `dry-schema`, `async`, `circuit_breaker`, no `frozen_string_literal` mandate
- **Standard Mode**: all other tasks — full conventions, `frozen_string_literal: true` on every file, Zeitwerk-compliant paths, `journald-logger` not `puts`, `Async {}` not `Thread.new`, `circuit_breaker` on external calls

### SKILL.md Size

Keep each SKILL.md under 500 lines. Move detailed reference material to `references/*.md` and link from SKILL.md. All reference links must be one level deep — no `references/sub/file.md`.

### Marketplace Manifest

When bumping the plugin version in `plugins/rubysmithing/.claude-plugin/plugin.json`, also update the `version` field in `.claude-plugin/marketplace.json` to keep them in sync.
