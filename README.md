# syncopated-context

<div align="center">

**Claude Code plugin marketplace for multi-domain development workflows**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.2.0-green.svg)](.claude-plugin/marketplace.json)
[![Ruby](https://img.shields.io/badge/ruby-3.4.4+-red)](.tool-versions)

</div>

---

## Features

- **Adaptive convention detection** — automatically detects Ruby conventions from `.rubocop.yml`, `standard` in Gemfile, or `.rubysmith` config; generates compliant code with explicit target stated
- **Multi-platform session recall** — aggregates AI interactions from Claude Code, Hermes, Gemini CLI, and OpenCode with temporal correlation and cross-platform synthesis  
- **Shared-root plugin architecture** — agents, references, and scripts shared across skills eliminate duplication while maintaining modularity
- **Convention mode switching** — single-file stdlib scripts receive minimal output; complex projects activate full conventions with Zeitwerk compliance and structured logging
- **Terminal UI scaffolding** — generates BubbleTea/Lipgloss/Huh interfaces from validated templates with complete keyboard handling and component hierarchy
- **LLM pipeline integration** — covers chatbots, tool-calling agents, vector search, DSPy reasoning modules, and MCP server scaffolding
- **GitHub activity correlation** — synchronizes session timelines with commit history and PR activity using `gh cli` integration
- **SIFT Protocol QA audits** — structured code quality reports with weighted rubrics and file:line evidence citations

---

## Installation

<details>
<summary>Claude Code — Plugin Marketplace (Recommended)</summary>

Install the complete plugin suite:
```bash
claude plugin add syncopated-context
```

Or install individual plugins:
```bash
claude plugin add syncopated-context/rubysmithing
claude plugin add syncopated-context/notebook
```

After installation, all skills become available in any Claude Code session.

</details>

<details>
<summary>Manual Installation from Source</summary>

```bash
git clone https://github.com/b08x/syncopated-context
cd syncopated-context

# Install both plugins
claude plugin add ./plugins/rubysmithing
claude plugin add ./plugins/notebook
```

</details>

<details>
<summary>Development Environment (Contributors)</summary>

Requires Ruby 3.4.4+ via asdf or rbenv:

```bash
cd plugins/rubysmithing
bundle install
```

For bash plugin development:
```bash
# Install dependencies
brew install shellcheck bats-core gum
# or
sudo apt install shellcheck bats gum
```

</details>

---

## Usage

### Command Synopsis

```bash
# Ruby development workflows
rubysmithing:plan           # Hub orchestrator for all Ruby tasks
rubysmithing:scaffold       # Project initialization via rubysmith/gemsmith
rubysmithing:refactor       # Convention fixes and Zeitwerk compliance
rubysmithing:genai          # LLM, RAG, embeddings, MCP servers
rubysmithing:tui            # Terminal UI scaffolding

# Multi-platform session analysis
recall yesterday            # Cross-platform session retrieval
recall --github owner/repo  # Correlate with GitHub activity
recall platform:claude debugging session

# Repository-level workflows  
/implement                  # Implementation planning and execution
/refactor                   # Code refactoring workflows
/containerize              # Docker deployment automation
```

### Ruby Development Options

#### Basic Operations
- `rubysmithing:analyse`: Static analysis with Gemba Walk methodology and root-cause tracing
- `rubysmithing:context`: Gem API verification using Context7 MCP with SQLite caching
- `rubysmithing:sift`: QA audits with weighted rubric and evidence citations
- `rubysmithing:yardoc`: Documentation generation with type inference

#### Advanced Workflows
- `rubysmithing:genai`: LLM and RAG pipeline scaffolding
- `rubysmithing:tui`: BubbleTea/Lipgloss terminal interface generation
- `rubysmithing:scaffold`: New project initialization with convention detection

### Session Recall Options

#### Platform-Specific Recall
- `recall platform:hermes <query>`: Search Hermes session database
- `recall platform:gemini <query>`: Parse Gemini CLI session files  
- `recall platform:opencode <query>`: Analyze OpenCode structured logs

#### Integrated Analysis
- `--github <owner/repo>`: Correlate sessions with commit history
- `--backup <path>`: Include restic backup diff analysis
- `<timeframe>`: Natural language time expressions (yesterday, last week, 2025-03-25)

### Examples

**Ruby Project Scaffolding:**
```bash
# Generate convention-compliant Ruby project
rubysmithing:scaffold -- cli tool for API monitoring with circuit breakers

# Build terminal dashboard with TUI framework
rubysmithing:tui -- two-panel interface: file browser left, content preview right
```

**Code Quality Analysis:**
```bash
# Run comprehensive QA audit
rubysmithing:sift -- audit lib/ directory

# Perform root-cause analysis on failing tests
rubysmithing:analyse -- trace spec/models/user_spec.rb failures
```

**Cross-Platform Session Analysis:**
```bash
# Reconstruct work across all platforms
recall authentication refactor last month

# Correlate development activity with GitHub
recall --github myorg/project --backup ~/Workspace database migration

# Synthesize debugging sessions  
recall platform:claude platform:hermes schema validation errors
```

---

## Plugin Architecture

### rubysmithing (Ruby Development Suite)

Shared-root pattern with 15 specialized agents handling distinct development domains:

```
rubysmithing/
├── agents/                     # Specialized development roles
│   ├── context-engineer.md     # Gem API verification and caching
│   ├── cognitive-architect.md  # System design and patterns
│   ├── ruby-diagnostics-engineer.md # Debugging and analysis
│   └── [12 other domain experts]
├── commands/                   # Workflow orchestration
│   ├── context.md              # API verification workflow
│   ├── audit.md                # Quality assessment commands  
│   └── flow.md                 # Development pipeline management
├── references/                 # Shared knowledge base
│   ├── gem-registry.md         # Curated gem recommendations
│   ├── design-patterns.md      # Ruby architecture patterns
│   └── genai-patterns.md       # LLM integration patterns
├── scripts/                    # Automation utilities
│   └── context_cache.rb        # SQLite gem API cache
└── skills/                     # Specialized capabilities
    ├── plan/                   # Hub orchestrator with routing logic
    ├── scaffold/               # Project initialization
    ├── genai/                  # LLM pipeline scaffolding
    └── [6 other specialized skills]
```

### notebook (Session Recall Suite)

Multi-platform extraction with correlation engines:

```
notebook/
├── skills/
│   ├── recall/
│   │   ├── scripts/
│   │   │   ├── multi-platform-extract.py    # Unified extraction across platforms
│   │   │   ├── extract-sessions.py          # Claude Code JSONL parser
│   │   │   └── session-graph.py             # NetworkX correlation analysis
│   │   └── workflows/
│   │       └── recall.md                    # Query routing and classification
│   └── notebooklm/                          # Document processing integration
└── templates/                               # Session analysis templates
```

---

## Configuration File

Plugin behavior can be customized through `.claude-plugin/settings.json` for repository-specific conventions or through individual plugin configurations for system-wide preferences.

### Ruby Conventions Configuration

```json
{
  "rubysmithing": {
    "convention_source": "rubocop",
    "default_mode": "standard", 
    "cache_ttl": 3600,
    "zeitwerk_compliance": true
  }
}
```

### Session Recall Configuration  

```json
{
  "notebook": {
    "platforms": ["claude", "hermes", "gemini"],
    "github_integration": true,
    "backup_correlation": true,
    "session_retention_days": 90
  }
}
```

### Configuration Options

#### Ruby Development
- `convention_source`: Detection method for Ruby conventions (rubocop, standard, rubysmith)
- `default_mode`: Convention enforcement level (lite, standard)
- `cache_ttl`: Gem API cache expiration in seconds
- `zeitwerk_compliance`: Enforce autoloader-compatible file structure

#### Session Recall
- `platforms`: Enabled session sources for recall analysis
- `github_integration`: Include GitHub activity correlation
- `backup_correlation`: Enable restic backup diff analysis
- `session_retention_days`: Local session cache retention period

---

## Convention Modes

Ruby development tasks automatically select between two convention enforcement levels before generating output.

### Lite Mode

Activates for single-file requests under ~50 lines using stdlib dependencies. Minimal requirements:
- No external gem dependencies beyond stdlib
- Optional `frozen_string_literal` pragma
- Basic error handling without circuit breakers
- Simple logging via built-in mechanisms

### Standard Mode  

Default for multi-file projects or those requiring external dependencies. Full convention enforcement:

| Convention | Requirement |
|------------|-------------|
| **Magic comment** | `# frozen_string_literal: true` on every file |
| **Autoloading** | Zeitwerk-compliant path ↔ class name mapping |
| **Utility modules** | `module_function` over `extend self` |
| **Logging** | Structured logging via `journald-logger` |
| **Concurrency** | `Async {}` fiber blocks for I/O operations |
| **External calls** | `circuit_breaker` wrapping for API calls |
| **Method signatures** | Keyword arguments for 3+ parameters |

Convention detection cascade: `.rubocop.yml` → `standard` in Gemfile → `.rubysmith` config → community standards.

---

## Platform Support

### AI Session Sources

| Platform | Storage Location | Export Method | Format |
|----------|------------------|---------------|--------|
| **Claude Code** | `~/.claude/projects/*/` | Native JSONL parsing | JSONL |
| **Hermes** | SQLite database | `hermes sessions export` | JSONL |  
| **Gemini CLI** | `~/.config/gemini/sessions/` | JSON file parsing | JSON |
| **OpenCode** | `~/.config/opencode/logs/` | Log file parsing | Structured logs |

### External Integrations

- **GitHub** — commit correlation, PR activity analysis via `gh cli`
- **Restic** — backup diff analysis and file evolution tracking  
- **NotebookLM** — document processing and research artifact import
- **Context7 MCP** — real-time gem API verification and caching

---

## Contributing

Issues and pull requests welcome. Run `bundle exec rubocop` and `bundle exec rspec` from `plugins/rubysmithing/` before submitting; `bundle exec git-lint` validates commit message format.

## License

[MIT](LICENSE) — Robert Pannick