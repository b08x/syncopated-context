# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a multi-plugin Claude Code marketplace repository called **syncopated-context**. It distributes multiple specialized development plugins:

- **rubysmithing** — Convention-aware Ruby development suite with 13 specialized agents
- **bashsmithing** — Bash development suite with shellcheck, BATS testing, and TUI scaffolding  
- **notebook** — Multi-platform AI session recall and analysis tools

The marketplace manifest is at `.claude-plugin/marketplace.json`. Individual plugins live under `plugins/*/`. The repository also contains many repository-level skills and commands that support broader development workflows.

## Repository Structure

```
syncopated-context/
├── .claude-plugin/marketplace.json     # Marketplace distribution manifest
├── commands/                           # Repository-level workflow commands
│   ├── implement.md, refactor.md       # Development workflow commands
│   ├── session-start.md, session-end.md # Session management
│   ├── containerize.md                 # Container deployment workflows
│   └── gemini/                         # Gemini CLI configurations
├── skills/                             # Repository-level skills
│   ├── containerization/               # Docker/container deployment
│   ├── ansible-collection-manager/     # Ansible automation
│   ├── resume-generator/               # Professional document generation
│   ├── recall/                         # AI session analysis and recall
│   └── [9 other specialized skills]    # Various development domains
├── plugins/
│   ├── rubysmithing/                   # Ruby development suite
│   ├── bashsmithing/                   # Bash development suite  
│   └── [future plugins]
└── tasks/                              # Task definitions and pre-flight reviews
```

## Common Development Commands

### Repository-Level Commands
```bash
# Plugin installation and management
claude plugin add syncopated-context                    # Install all plugins
claude plugin add syncopated-context/rubysmithing      # Install specific plugin  

# Repository-level workflow commands (from commands/)
/implement     # Implementation planning and execution
/refactor      # Code refactoring workflows
/containerize  # Docker containerization workflows
/session-start # Start development session with context setup
/session-end   # End session with cleanup and documentation

# Memory and recall management
/setup-memory  # Initialize persistent memory system
/recall        # Multi-platform AI session analysis
```

### Plugin-Specific Development

#### rubysmithing (Ruby Development)
All commands run from `plugins/rubysmithing/`:

```bash
# Ruby environment setup
ruby --version  # Should be 3.4.4+ (see .tool-versions)
bundle install  # Install Ruby dependencies

# Development workflow
bundle exec rubocop              # Lint all Ruby code
bundle exec rubocop -a           # Lint with autocorrect
bundle exec rspec                # Run all tests  
bundle exec rspec spec/path/to/file_spec.rb  # Single test file
bundle exec git-lint             # Validate commit messages

# Skills available
rubysmithing:plan       # Hub/orchestrator for all Ruby tasks
rubysmithing:analyse    # Code analysis (Gemba Walk, Five Whys)
rubysmithing:scaffold   # Project initialization via rubysmith
rubysmithing:refactor   # Convention fixes, Zeitwerk compliance
rubysmithing:genai      # LLM, RAG, embeddings integration
rubysmithing:tui        # Terminal UI development
rubysmithing:sift       # QA audits with weighted rubrics
rubysmithing:yardoc     # Documentation generation
```

#### bashsmithing (Bash Development)
```bash
# Development workflow
shellcheck scripts/**/*.sh       # Bash linting
bats test/**/*.bats              # BATS testing framework

# Skills available  
bashsmithing:scaffold   # Bash project initialization with Gum/Charm
bashsmithing:tui        # Terminal UI scaffolding
bashsmithing:context    # Context caching and management
```

## Plugin Architecture

### rubysmithing (Ruby Development Suite)

Uses **shared-root architecture** — agents, references, and scripts used by multiple skills live at the plugin root:

```
plugins/rubysmithing/
├── .claude-plugin/plugin.json   # Plugin metadata (v2.2.0)
├── agents/                      # 15 specialized agents including systems-observer, agentic-data-engineer
├── commands/                    # Shared commands (context, audit, flow, diagnose)  
├── references/                  # Shared references (gem-registry, design-patterns)
├── scripts/                     # Shared scripts (context_cache.rb — SQLite gem cache)
├── assets/skeleton/             # TUI project skeleton templates
├── skills/                      # 9 specialized skills (plan, analyse, scaffold, etc.)
├── Gemfile                      # Ruby dependencies
└── .rubocop.yml                 # RuboCop config (Ruby 3.4+)
```

Skills reference shared resources via `$CLAUDE_PLUGIN_ROOT/agents/`, `$CLAUDE_PLUGIN_ROOT/references/`, etc.

### bashsmithing (Bash Development Suite)

Convention-aware Bash development with shellcheck integration and Gum/Charm TUI scaffolding.

## Repository-Level Skills Architecture

Beyond plugin-specific skills, the repository provides many standalone skills for broader development workflows:

### Core Development Skills
- **containerization/** — Docker deployment and container orchestration
- **ansible-collection-manager/** — Ansible automation and infrastructure as code  
- **recall/** — Multi-platform AI session analysis and extraction (14 files, 256KB)
- **readme-generator/** — Automated documentation generation
- **tech-interview-prep/** — Technical interview preparation and coding challenges

### Specialized Domain Skills  
- **resume-generator/** — Professional document generation (15 files, 140KB)
- **servicenow-kb-generator/** — ServiceNow knowledge base automation
- **ruby-design-patterns/** — Advanced Ruby architecture patterns
- **jekyll-react-islands/** — Static site generation with React components
- **notebooklm/** — NotebookLM integration for research and analysis

### Development Toolchain

#### Ruby Environment (for rubysmithing plugin)
Ruby version: **3.4.4** (`.tool-versions` / `.ruby-version`)  
See Plugin-Specific Development commands above for Ruby workflow.

#### Bash Environment (for bashsmithing plugin) 
Requires: `shellcheck`, `bats-core`, `gum` (Charm CLI tools)

#### General Dependencies
- Claude Code CLI for plugin management
- Git for version control  
- Docker for containerization workflows

## Plugin and Skill Development

### Skill Authoring Standards

All skills (repository-level and plugin-specific) follow these conventions:

- **Frontmatter**: Only `name` (≤64 chars) and `description` (≤1024 chars, third person)  
- **Size limit**: Keep SKILL.md under 500 lines
- **References**: Move detailed reference material to `references/*.md`, one level deep only
- **Agent integration**: Use Agent tool for complex multi-step workflows

### Resource Organization

#### Repository-Level Skills (`skills/*/`)
- Self-contained with their own `references/`, `scripts/`, `templates/` subdirectories
- No shared dependencies — each skill manages its own resources

#### Plugin Skills (`plugins/*/skills/*/`)  
- **Shared resources** (at plugin root): agents, references, scripts used by multiple skills
- **Skill-local resources**: used only within one skill, kept in skill subdirectories
- Reference shared resources via `$CLAUDE_PLUGIN_ROOT/path/to/resource.md`

### Convention Modes (rubysmithing plugin)

- **Lite Mode**: Single-file ≤~50 lines, stdlib only, minimal dependencies
- **Standard Mode**: Full conventions, `frozen_string_literal: true`, Zeitwerk compliance, structured logging

### Hub-and-Spoke Pattern (rubysmithing plugin)

The `rubysmithing:plan` skill acts as an orchestrator that detects task types and delegates to specialized agents. Agents are discovered at `$CLAUDE_PLUGIN_ROOT/agents/` (shared) or skill-local agent directories.

### Marketplace Management

#### Version Synchronization
When updating plugin versions:
1. Update individual plugin version in `plugins/<name>/.claude-plugin/plugin.json`  
2. Update marketplace version in `.claude-plugin/marketplace.json`
3. Ensure version compatibility across all distributed plugins

#### Distribution Structure
- **Marketplace manifest**: `.claude-plugin/marketplace.json` — distributes all plugins as a bundle
- **Individual plugins**: Each has its own `plugin.json` for standalone installation
- **Repository-level skills**: Automatically available after any plugin installation from this marketplace

## Context7 MCP Documentation Access

### Use Context7 MCP for Loading Documentation

Context7 MCP is available to fetch up-to-date documentation with code examples.

**Recommended library IDs**:

- `/open-gitagent/gitagent` - Framework-agnostic, git-native standard for defining AI agents with version control, compliance management, and portable deployment across multiple LLM frameworks (669 code snippets, High reputation, Score: 76.5)
