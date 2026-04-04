# syncopated-context

<div align="center">

**GitAgent-compliant development ecosystem for cross-platform AI session synthesis and automated engineering workflows**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitAgent Spec](https://img.shields.io/badge/GitAgent-0.1.0-blue.svg)](agent.yaml)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](agent.yaml)
[![Python](https://img.shields.io/badge/python-3.12+-red)](.python-version)

</div>

---

## Features

- **GitAgent Specification Compliance** — adheres to the v0.1.0 standard for version-controlled AI agent definitions
- **Harness-Agnostic Operation** — maintains consistent skill availability across multiple AI harnesses with unified interface standards
- **Multi-Platform Session Synthesis** — aggregates interactions from disparate AI platforms with temporal correlation and unified analysis
- **Deterministic Implementation Strategy** — executes feature adaptation through a 5-phase workflow with mandatory planning and state persistence
- **Linguistic Agent Personas** — employs Systemic Functional Linguistics (SFL) archetypes for specialized engineering and architectural oversight
- **Universal Rule System** — enforces directory-agnostic path resolution and normalized date/time handling across all runtimes
- **Convention-Aware Automation** — detects project-specific configurations (RuboCop, StandardRB) to adapt output behavior dynamically

---

## Architecture

The ecosystem is structured as a modular meta-harness, separating core agent definitions from specialized capability modules and legacy integrations.

```text
syncopated-context/
├── agent.yaml                 # GitAgent v0.1.0 manifest
├── SOUL.md                    # Agent identity and marketplace context
├── RULES.md                   # Universal behavioral and technical constraints
├── skills/                    # 25 specialized capability modules
│   ├── implement/             # Phase-based feature adaptation
│   ├── recall/                # Cross-platform session analysis
│   └── [23 other skills]      # Domain-specific automation
├── tools/                     # MCP-compatible YAML schemas
│   ├── multi-platform-recall  # Unified session extraction
│   └── [other tools]          # External service integrations
├── plugins/                   # Legacy plugin suites
│   ├── rubysmithing/          # SFL-persona based Ruby development
│   └── bashsmithing/          # Shellcheck-integrated Bash automation
└── tasks/                     # Implementation definitions and reviews
```

---

## Installation

<details>
<summary>Claude Code</summary>

```bash
# Install as GitAgent specification
claude agent add https://github.com/b08x/syncopated-context

# Or install legacy plugin bundle (deprecated)
claude plugin add syncopated-context
```

</details>

<details>
<summary>Hermes</summary>

```bash
# Clone and configure as agent
git clone https://github.com/b08x/syncopated-context
hermes agent add ./syncopated-context
```

</details>

<details>
<summary>Gemini CLI</summary>

```bash
# Install agent specification
gemini agent install https://github.com/b08x/syncopated-context
```

</details>

<details>
<summary>OpenCode</summary>

```bash
# Add to agent registry
opencode add-agent syncopated-context https://github.com/b08x/syncopated-context
```

</details>

<details>
<summary>Manual Installation</summary>

```bash
git clone https://github.com/b08x/syncopated-context
cd syncopated-context

# Install Python dependencies
uv sync

# Verify installation
python main.py --help
```

</details>

---

## Usage

### Command Synopsis

The agent is invoked via the standard harness-specific prefixes (e.g., `/` or `!`). Core workflows follow a plan-execute-validate lifecycle.

```bash
# Session Analysis
/recall [platform] [timeframe] [topic]

# Feature Implementation
/implement [source_url_or_path] -- [description]

# Code Refactoring
/refactor [path] -- [instruction]
```

### Options

**Recall (Session Extraction)**
- `--platform`: Target platform (claude-code, gemini-cli, opencode, hermes, all)
- `--timeframe`: Extraction window (today, yesterday, last-week, last-month)
- `--topic`: Optional keyword filter for semantic pruning

**Implement (Feature Adaptation)**
- `--new`: Force initialization of a fresh implementation plan
- `--resume`: Continue from the last recorded checkpoint in `implement/state.json`
- `--status`: Display current implementation progress and pending tasks

### Examples

**Multi-Platform Correlation:**
```bash
# Analyze sessions across all platforms regarding database migrations
/recall --platform all --timeframe last-week --topic "postgres migration"
```

**Systematic Implementation:**
```bash
# Port a feature from a remote repository with architecture adaptation
/implement https://github.com/user/repo -- adapt auth service to use local Redis cache
```

**Ruby Architectural Oversight:**
```bash
# Invoke the SFL-persona based Ruby orchestrator
/rubysmithing:plan Write a Sequel-backed data pipeline with async processing
```

---

## Technical Standards

### Path Resolution
Resolution must be directory-agnostic. All scripts utilize `Path(__file__)` or platform-equivalents to resolve resource paths relative to their own location rather than the current working directory.

### Session Persistence
The `implement` skill maintains state in the project root under the `implement/` directory:
- `plan.md`: The structured implementation checklist and architectural mapping.
- `state.json`: The machine-readable checkpoint and progress tracker.

### Agent Personas
Specialized agents in the `rubysmithing` suite employ distinct personas to minimize "the telephone game" during task delegation:
- **The Bureaucrat**: Decisive orchestration and routing.
- **Other Steve**: Adversarial architectural translation and blueprinting.
- **The Code Janitor**: Pedantic convention compliance and refactoring.

---

## Contributing

Contributions are welcome via issues and pull requests. Submissions must adhere to the GitAgent specification guidelines. Run the validation suite before submitting:

```bash
python scripts/validate-migration.py  # Validate GitAgent compliance
python scripts/test-skills.py         # Verify skill functionality
```

## License

[MIT](LICENSE)
