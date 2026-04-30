# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the **rubysmithing plugin** v2.1.0 - a convention-aware Ruby development suite using shared-root architecture. It contains 15 specialized agents and 10 workflow skills for comprehensive Ruby development, from scaffolding to AI/NLP integration.

## Development Environment

### Ruby Requirements
- **Ruby Version**: 3.4.4 (defined in `.ruby-version`)
- **Dependency Management**: Bundler with locked dependencies in `Gemfile.lock`

### Essential Commands

```bash
# Environment setup
bundle install                               # Install all dependencies

# Development workflow
bundle exec rubocop                          # Lint entire codebase
bundle exec rubocop -a                       # Lint with autocorrect  
bundle exec rspec                            # Run full test suite
bundle exec rspec spec/path/to/file_spec.rb  # Run single test file
bundle exec git-lint                         # Validate commit messages

# Context management
ruby scripts/context_cache.rb list          # List cached gem APIs
ruby scripts/context_cache.rb clear         # Clear SQLite cache
```

## Architecture

### Shared-Root Pattern

Resources are organized for reuse across multiple skills:

```
plugins/rubysmithing/
├── agents/           # 15 specialized agents (shared across skills)
├── references/       # Shared design patterns, gem registry, TUI patterns
├── scripts/          # context_cache.rb (SQLite gem API verification)
├── assets/skeleton/  # TUI project templates
└── skills/          # 10 workflow skills
```

Skills reference shared resources via `$CLAUDE_PLUGIN_ROOT/path/to/resource.md`.

### Agent Ecosystem

| Agent Type | Purpose | Key Agents |
|:-----------|:--------|:-----------|
| **Orchestration** | Task routing and coordination | `agentic-operations-lead` |
| **Code Generation** | Convention-aware Ruby development | `agentic-software-engineer`, `platform-engineer` |
| **Quality Assurance** | Code review and compliance | `senior-qa-engineer`, `compliance-guardrail-agent` |
| **Specialized Domains** | AI/NLP, TUI, data engineering | `cognitive-architect`, `ux-engineer`, `agentic-data-engineer` |
| **Maintenance** | Refactoring and diagnostics | `maintenance-architect`, `ruby-diagnostics-engineer` |

### Hub-and-Spoke Workflow

The `/rubysmithing:plan` skill acts as the entry point orchestrator:
1. Detects task type and Ruby conventions
2. Flags non-stdlib gem usage for context verification  
3. Routes to appropriate specialist agents
4. Follows SADD tree-of-thoughts: context → design → verification

## Convention Modes

### Lite Mode
- **Target**: Single file ≤50 lines
- **Dependencies**: Ruby stdlib only
- **Structure**: Minimal, self-contained

### Standard Mode  
- **Target**: Full Ruby projects
- **Requirements**: `frozen_string_literal: true`, Zeitwerk compliance
- **Features**: Structured logging, circuit breakers, dry-rb integration

## Key Dependencies

### Core Runtime
- **zeitwerk**: Autoloading and code organization
- **sequel + sqlite3**: Database abstraction and caching
- **dry-struct + dry-types**: Type-safe data structures  
- **refinements**: Safe monkey-patching

### TUI Development
- **bubbletea**: Terminal UI framework (Bubble Tea port)
- **lipgloss**: Styling and layout

### AI/NLP Integration  
- Available through shared references and cognitive-architect agent
- Context verification for non-stdlib gems via SQLite cache

### Quality Assurance
- **RuboCop**: Comprehensive linting with 10+ extensions
- **RSpec**: Testing framework  
- **SimpleCov**: Code coverage
- **git-lint**: Commit message validation

## Quality Assessment

### SIFT Protocol
Use `/rubysmithing:sift` for architectural reviews with weighted rubrics:

```bash
/rubysmithing:sift Review this project and identify issues
/rubysmithing:sift --advisory for code quality assessment  
```

The SIFT protocol evaluates:
- **Structure**: Zeitwerk compliance, file organization
- **Idioms**: Ruby best practices, convention adherence  
- **Functionality**: Logic correctness, error handling
- **Testing**: Coverage, test quality, maintainability

### Diagnostic Analysis

Use `/rubysmithing:analyse` for root cause investigation:
- **Gemba Walk**: Understand unfamiliar code before refactoring
- **Muda Analysis**: Identify waste (dead code, over-engineering)
- **Root-Cause Tracing**: Debug errors back to original source
- **Five Whys**: Address systemic/recurring issues

## Development Workflow

### New Feature Development
1. `/rubysmithing:plan` - Orchestrate and route to specialist agents
2. Convention detection (Lite vs Standard mode)
3. Context verification for external dependencies
4. Implementation via specialized agents
5. Quality verification via SIFT protocol

### Refactoring
1. `/rubysmithing:analyse` - Understand current state  
2. `/rubysmithing:refactor` - Apply convention fixes
3. `/rubysmithing:sift` - Verify improvements

### TUI Applications
- Use `/rubysmithing:tui` for Bubble Tea scaffolding
- Templates available in `assets/skeleton/`
- Follows Charm CLI patterns with lipgloss styling

## Context Caching

The `scripts/context_cache.rb` maintains a SQLite database at `~/.rubysmithing/context_cache.db`:
- Caches gem API signatures for offline development
- Provides method resolution for non-stdlib dependencies
- Degrades gracefully when upstream APIs unavailable
- Persists across Claude Code session restarts

## Integration Points

### External Skills
- References shared `design-patterns.md`, `gem-registry.md`, `tui-patterns.md`
- Integrates with repository-level containerization and session management skills

### Quality Gates
- Pre-commit hooks via git-lint
- Continuous quality assessment via SIFT protocol  
- Convention compliance via Zeitwerk and RuboCop

This plugin embodies convention-over-configuration for Ruby development while providing escape hatches for specialized requirements through its agent ecosystem.