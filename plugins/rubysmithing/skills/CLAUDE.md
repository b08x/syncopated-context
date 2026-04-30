# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the **skills directory** within the rubysmithing plugin v2.1.0. It contains 10 specialized Ruby development skills that implement a hub-and-spoke architecture for convention-aware Ruby development.

## Skills Architecture

### Hub-and-Spoke Pattern

The `plan` skill acts as the central orchestrator, routing tasks to specialized sub-skills based on domain:

```
plan (hub) ──┬── analyse (diagnostics)
             ├── context (gem API verification)  
             ├── data-engineer (schema design)
             ├── genai (AI/NLP integration)
             ├── refactor (convention fixes)
             ├── scaffold (project init)
             ├── sift (QA assessment)
             ├── tui (terminal UI)
             └── yardoc (documentation)
```

### Delegation Rules

- **Single entry point**: Always start with `/rubysmithing:plan` for general Ruby code generation
- **Direct invocation**: Use specific skills directly only when you know the exact domain (e.g., `/rubysmithing:sift` for QA audits)
- **Agent delegation**: Skills delegate to shared agents at `$CLAUDE_PLUGIN_ROOT/agents/` for complex operations

## Development Commands

All commands run from the **parent plugin directory** (`../`):

```bash
# Development workflow
bundle install              # Install Ruby dependencies
bundle exec rubocop         # Lint all Ruby files  
bundle exec rubocop -a      # Lint with autocorrect
bundle exec rspec           # Run full test suite
bundle exec git-lint        # Validate commit messages

# Context management (plugin-level script)
ruby scripts/context_cache.rb list    # Show cached gem APIs
ruby scripts/context_cache.rb clear   # Clear SQLite cache
```

## Convention Detection System

The skills implement a sophisticated convention detection cascade:

1. **RuboCop config** (`.rubocop.yml`) - highest priority
2. **StandardRB** (`standard` in Gemfile) - second priority  
3. **Rubysmith presets** (`.rubysmith` file) - third priority
4. **Community idioms** (fallback) - default Ruby best practices

## Two-Mode Architecture

### Lite Mode
- **Triggers**: "quick script", "stdlib only", single file ≤50 lines
- **Constraints**: Pure Ruby stdlib, no external gems
- **Output**: Single file with minimal dependencies

### Standard Mode  
- **Default** for all multi-file tasks
- **Requirements**: `frozen_string_literal: true`, Zeitwerk compliance
- **Stack**: Full convention stack (async, circuit_breaker, dry-schema, etc.)

## Resource Referencing

Skills use a shared-resource architecture:

### Shared Resources (at plugin root)
```bash
$CLAUDE_PLUGIN_ROOT/agents/           # 13 specialized agents
$CLAUDE_PLUGIN_ROOT/references/       # Shared documentation  
$CLAUDE_PLUGIN_ROOT/scripts/          # SQLite cache CLI
$CLAUDE_PLUGIN_ROOT/assets/           # TUI skeletons
```

### Skill-Local Resources
```bash
skills/<name>/references/             # Skill-specific docs
skills/<name>/commands/               # Skill workflows
```

## Key Skills and Use Cases

| Skill | Primary Use Case | Key Features |
|:------|:-----------------|:-------------|
| `plan` | General Ruby code generation | Hub orchestrator, convention detection |
| `analyse` | Diagnostics and debugging | Gemba Walk, Muda Analysis, Five Whys |
| `sift` | Code quality assessment | SIFT Protocol V1.0, 8-section reports |
| `context` | Gem API verification | SQLite-cached resolution via Context7 MCP |
| `refactor` | Convention compliance | AST-targeted rewrites, do-and-judge loops |
| `tui` | Terminal UI development | BubbleTea/Charm ecosystem scaffolding |
| `genai` | AI/NLP integration | LLM, RAG, embeddings, MCP servers |

## Error Contract System

All skills follow a structured error contract defined in `plan/references/error-contract.md`:
- Agents return `[AGENT ERROR]` blocks rather than bare failures
- Structured error propagation enables retry logic
- Separation of concerns between orchestration and execution

## Workflow Integration

Skills integrate with parent plugin workflows via commands:
- `/rubysmithing:audit` - SIFT assessment with rubric scoring
- `/rubysmithing:diagnose` - Full diagnostic + fix workflow  
- `/rubysmithing:flow` - Context + implementation + verification
- `/rubysmithing:translate` - Foreign codebase translation to Ruby

## Context Caching

The plugin maintains a SQLite cache at `~/.rubysmithing/context_cache.db` for gem API resolution:
- Persists across sessions
- Graceful degradation when APIs unavailable  
- Accessed via `scripts/context_cache.rb` CLI

## Development Principles

- **Convention over configuration**: Auto-detect project conventions
- **Separation of powers**: Orchestrators don't implement, implementers don't orchestrate
- **Graceful degradation**: Always produce code even with incomplete context
- **Evidence-based QA**: All quality assessments include file:line evidence