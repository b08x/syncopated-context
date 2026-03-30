<div align="center">

# rubysmithing

Convention-aware Ruby development suite for Claude Code — thirteen specialized agents covering code generation, TUI scaffolding, AI/NLP integration, refactoring, QA auditing, and foreign codebase translation.

![Version](https://img.shields.io/badge/version-2.1.0-blue)
![Ruby](https://img.shields.io/badge/ruby-3.4.4-red)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

</div>

---

## Features

- **Convention-locked code generation** — detects `.rubocop.yml`, `standard` in Gemfile, or `.rubysmith` presets automatically; every generated file calibrates to the detected target
- **Dual execution modes** — Lite Mode for stdlib-only scripts under 50 lines; Standard Mode for the full production stack with `frozen_string_literal`, Zeitwerk, `Async {}`, and `circuit_breaker`
- **Verified gem API resolution** — the Context agent resolves live method signatures via Context7 MCP before library-specific code generation, with SQLite-backed caching across session restarts
- **Parallel agent dispatch** — compound requests decompose and dispatch to independent agents concurrently
- **Closed-loop evaluation** — the Meta-Judge generates rubric specs before refactoring; the Judge evaluates output against those specs with file:line evidence; the Refactor agent retries until scores pass
- **Structured diagnostic framework** — the Analyse agent applies Gemba Walk, Muda Analysis, Root-Cause Tracing, or Five Whys depending on problem type; findings persist to a scratchpad for downstream handoff
- **Foreign codebase translation** — the Deconstructor produces Zeitwerk-compliant Ruby blueprints from Python, React, and Go sources, with explicit GIL and GC impact notes
- **Full SIFT QA reporting** — eight-section quality assessments anchored to the Toulmin evidence framework, with optional SADD-integrated verification footer

---

## Skills

| Skill | Activation | What it does |
|:------|:-----------|:-------------|
| `plan` | Code generation outside specialized domains | Hub orchestrator — detects conventions, dispatches to spoke agents, enforces error contracts |
| `analyse` | "root cause", "dead code", "muda", "gemba", Zeitwerk NameError | Gemba Walk, Muda Analysis, Root-Cause Tracing, Five Whys; produces keyed findings for refactor handoff |
| `refactor` | "refactor", "fix conventions", "Zeitwerk compliance" | Convention-targeted rewrites with optional do-and-judge retry loop |
| `sift` | "assess", "audit", "SIFT", "tech advisory", "what's wrong" | SIFT Protocol V1.0 QA reports — Full Report, System Design Review, Tech Advisory, Backlog modes |
| `scaffold` | "new project", rubysmith, gemsmith, "scaffold a tool" | Project initialization via rubysmith/gemsmith CLI with archetype presets |
| `yardoc` | `@param`, `@return`, "yardoc", "document this code" | YARD documentation via AST analysis and type inference |
| `genai` | LLM, RAG, chatbot, DSPy, MCP server, embeddings, pgvector | AI/NLP component scaffolding — ruby_llm, dspy.rb, fast-mcp, pgvector+sequel pipelines |
| `tui` | BubbleTea, Lipgloss, Huh, Gum, NTCharts, "terminal UI" | Terminal UI scaffolding using the Ruby Charm/Bubble ecosystem |
| `context` | Prerequisite when non-stdlib gems are in scope | Gem API verification via Context7 MCP; SQLite-cached results with graceful degradation |
| `data-engineer` | Schema design, data modeling, SQL pipelines | SADD tree-of-thoughts for schema authoring with context, design, and verification steps |

---

## Agent Architecture

The suite runs thirteen specialized agents organized into five layers. Each agent carries an SFL-derived behavioral persona that enforces its operational role.

### Orchestration & Control

| Agent | Role | Persona |
|:------|:-----|:--------|
| `agentic-operations-lead` | Entry point; routing, convention detection, parallel dispatch | The Bureaucrat — decisive, strict |

### Generation & Production

| Agent | Role | Persona |
|:------|:-----|:--------|
| `agentic-software-engineer` | General Ruby code generation (Lite/Standard modes) | The Generalist — pragmatic, tireless |
| `cognitive-architect` | AI/NLP component scaffolding | The Visionary — structured, modern |
| `ux-engineer` | Terminal UI scaffolding | The Aestheticist — design-oriented, state-obsessed |
| `platform-engineer` | Project initialization | The Future-Proof Visionary — foundational, optimistic |
| `context-engineer` | Gem API verification and SQLite caching | The Epistemic Verifier — skeptical, rigorous |

### Diagnostic & Remediation

| Agent | Role | Persona |
|:------|:-----|:--------|
| `ruby-diagnostics-engineer` | Root-cause analysis, Gemba Walk, Muda identification | The Stealth Debugger — inquisitive, paranoid |
| `maintenance-architect` | Convention-targeted rewrites, Zeitwerk compliance, do-and-judge loops | The Code Janitor — pedantic, relentless |

### Governance & Evaluation

| Agent | Role | Persona |
|:------|:-----|:--------|
| `director-of-ai-risk` | Pre-evaluation YAML rubric specification | The Specifier — risk-averse, rigid |
| `compliance-guardrail-agent` | Rubric application with file:line evidence, PASS/FAIL verdict | The Evaluator — punitive, strict |
| `senior-qa-engineer` | SIFT Protocol QA reports, architectural reviews | The Pragmatist — analytical, holistic |

### Documentation & Translation

| Agent | Role | Persona |
|:------|:-----|:--------|
| `developer-experience-engineer` | YARD documentation via AST analysis and type inference | The Semantic Inferencer — academic, precise |
| `senior-backend-architect` | Foreign codebase → Ruby OOP blueprint (Python, React, Go) | "Other Steve" — weary, adversarial, anti-slop |

The orchestrator never implements code directly. The meta-judge never evaluates artifacts. The deconstructor never writes implementation. Separation of powers is structural.

---

## Installation

<details>
<summary>Claude Code — Marketplace Install (Recommended)</summary>

```bash
claude plugin install rubysmithing
```

After installation, invoke any skill by name:

```bash
/rubysmithing:plan
/rubysmithing:analyse
/rubysmithing:refactor
/rubysmithing:sift
/rubysmithing:scaffold
/rubysmithing:yardoc
/rubysmithing:genai
/rubysmithing:tui
/rubysmithing:context
/rubysmithing:data-engineer
```

</details>

<details>
<summary>Local Development Install</summary>

```bash
git clone https://github.com/rwpannick/rubysmithing-plugin
cd rubysmithing-plugin/plugins/rubysmithing
bundle install
```

</details>

---

## Usage

### Basic Invocation

```bash
# Convention-aware code generation
/rubysmithing:plan Write a Sequel-backed data pipeline with async processing

# Root cause analysis
/rubysmithing:analyse NameError: uninitialized constant MyApp::Data::Processor

# Convention-targeted refactoring
/rubysmithing:refactor lib/app/processor.rb

# Quality assessment
/rubysmithing:sift Review this project and identify issues
```

### Examples

#### Code Generation

```bash
/rubysmithing:plan Write a Sequel-backed data pipeline with async processing and circuit breaker wrapping
```

The orchestrator detects conventions, flags non-stdlib gems, runs the context agent for API verification, then delegates to `agentic-software-engineer`.

#### Analysis & Diagnostics

```bash
/rubysmithing:analyse I keep getting NameError: uninitialized constant MyApp::Data::Processor
```

The analyse agent traces the Zeitwerk load path, identifies the constant → file path mismatch, and keys the finding to a pattern in `refactor-patterns.md` for handoff.

```bash
/rubysmithing:analyse This codebase feels bloated — half the methods seem unused
```

Triggers Muda Analysis: maps seven Ruby waste types (dead methods, unused gems, over-processing, stale flags) across the target directory.

#### Refactoring

```bash
/rubysmithing:refactor lib/app/processor.rb
```

Convention scan → AST-targeted rewrites → optional do-and-judge retry loop for critical files.

#### QA Assessment

```bash
/rubysmithing:sift Review this project and tell me what's wrong
```

Full SIFT V1.0 report: eight sections, Toulmin evidence anchoring, optional SADD verification footer.

#### TUI Scaffolding

```bash
/rubysmithing:tui Build a BubbleTea monitoring dashboard for my RAG pipeline metrics
```

Runs `context-engineer` as a prerequisite, then generates the full BubbleTea application skeleton: `app.rb`, screen definitions, `Components::Base` adapters, Lipgloss styles.

#### Schema Design

```bash
/rubysmithing:data-engineer Design a schema for a multi-tenant SaaS with users, organizations, and billing
```

SADD tree-of-thoughts workflow: context gathering → conceptual design → verification against requirements.

#### Foreign Codebase Translation

```bash
/rubysmithing:plan Translate this Python FastAPI service to Ruby
```

Routes to `senior-backend-architect`: surveys the source, maps paradigms (decorators → `Module#prepend`, dataclasses → `Struct.new(keyword_init: true)`), produces a Zeitwerk-compliant Blueprint, Object Graph, and Translation Map with confidence ratings.

---

## Convention Modes

### Lite Mode

Triggers on: "quick script", "no dependencies", "stdlib only", single-file output under ~50 lines.

- Pure Ruby stdlib — no `dry-schema`, `async`, `circuit_breaker`
- `frozen_string_literal` recommended but not enforced
- Single file; brief inline comment for non-obvious choices

### Standard Mode

Default for all other tasks. Multi-file requests always use Standard Mode regardless of individual file line count.

Every generated file applies:

```ruby
# frozen_string_literal: true
```

Full convention stack:

- Zeitwerk-compliant path ↔ class name mapping
- `module_function` over `extend self`
- `Async { }` over `Thread.new`
- `circuit_breaker` wrapping on all external API calls
- `journald-logger` over `puts` / `p` / `pp`
- `Struct.new(keyword_init: true)` for value objects
- Keyword args for methods with 3+ parameters
- Guard clauses over nested conditionals

---

## Gem API Cache

The context agent maintains a SQLite database at `~/.rubysmithing/context_cache.db`. Resolved gem signatures persist across session restarts and degrade gracefully when upstream APIs are unavailable.

```bash
# Check cache status for a gem
ruby scripts/context_cache.rb fetch ruby_llm --json

# Store a resolved entry manually
ruby scripts/context_cache.rb store ruby_llm /crmne/ruby_llm '[".chat(...)"]' 'RubyLLM.chat'

# List all cached gems
ruby scripts/context_cache.rb list

# Force a fresh lookup
ruby scripts/context_cache.rb evict ruby_llm
```

Degradation order: fresh cache → stale cache (with `#stale-cache` annotation) → unverified fallback (with `#WARNING: Unverified API Syntax` comments). The cache never blocks code generation; it annotates uncertainty instead.

> **📖 Full Documentation:** See `references/cache-cli.md` for complete exit codes and `--json` output shapes. See `references/gem-registry.md` for the curated Context7 ID mapping covering ~40 gems in the stack.

---

## Plugin Structure

```
plugins/rubysmithing/
├── .claude-plugin/plugin.json   # Plugin metadata (name, version, description)
├── agents/                      # All 13 agents — shared at plugin root
│   ├── agentic-operations-lead.md
│   ├── agentic-software-engineer.md
│   ├── context-engineer.md
│   ├── cognitive-architect.md
│   ├── ux-engineer.md
│   ├── platform-engineer.md
│   ├── ruby-diagnostics-engineer.md
│   ├── maintenance-architect.md
│   ├── director-of-ai-risk.md
│   ├── compliance-guardrail-agent.md
│   ├── senior-qa-engineer.md
│   ├── developer-experience-engineer.md
│   ├── agentic-data-engineer.md
│   └── senior-backend-architect.md
├── commands/                    # Workflow commands
│   ├── context.md
│   ├── flow.md
│   ├── schema.md
│   └── vibe.md
├── references/                  # Shared reference docs
│   ├── gem-registry.md          # Context7 ID → gem mapping with architectural roles
│   ├── cache-cli.md             # context_cache.rb CLI reference
│   ├── genai-patterns.md       # Verified AI/NLP implementation patterns
│   ├── design-patterns.md       # TUI layout paradigms and design system
│   └── tui-patterns.md         # Bubble ecosystem component patterns
├── scripts/
│   └── context_cache.rb         # SQLite-backed gem API cache CLI
├── tasks/                       # Workflow task chains
│   ├── schema/                  # SADD schema workflow steps
│   └── vibe/                    # Vibe analysis task steps
├── assets/
│   └── skeleton/                # TUI project skeleton (copied per scaffold)
├── skills/
│   ├── plan/                    # Hub orchestrator; error-contract.md + conventions
│   ├── analyse/                 # Methods, scratchpad scripts
│   ├── context/                 # SKILL.md only — agent and refs at plugin root
│   ├── data-engineer/           # SKILL.md + task chain references
│   ├── genai/                   # SKILL.md only — agent and refs at plugin root
│   ├── refactor/                # Refactor patterns, do-and-judge integration
│   ├── scaffold/                # scaffold-patterns.md
│   ├── sift/                    # SIFT Protocol docs, templates, schema
│   ├── tui/                     # SKILL.md only — agent, refs, assets at plugin root
│   └── yardoc/                  # YARD patterns
├── Gemfile
├── .rubocop.yml                 # RuboCop config (Ruby 3.4)
└── .tool-versions               # Ruby 3.4.4 via asdf
```

### Shared vs Skill-Local Resources

Resources used by two or more skills live at the plugin root and are referenced via absolute path:

```
$CLAUDE_PLUGIN_ROOT/agents/context-engineer.md
$CLAUDE_PLUGIN_ROOT/references/gem-registry.md
$CLAUDE_PLUGIN_ROOT/scripts/context_cache.rb
```

Resources exclusive to one skill stay inside `skills/<name>/` and use relative paths from `SKILL.md`:

```
references/refactor-patterns.md
agents/maintenance-architect.md
```

Never mix. A relative path from `skills/genai/SKILL.md` resolves to `skills/genai/references/`, not the plugin root.

---

## Skill Authoring

### SKILL.md Frontmatter

Two fields only:

```yaml
---
name: skill-name          # ≤64 characters
description: Third-person description of what the skill does and when to activate it.  # ≤1024 characters
---
```

Description must be third-person — it is injected into Claude's system prompt and point-of-view consistency matters for reliable activation.

### Error Contract

Sub-agents return structured `[AGENT ERROR]` blocks rather than bare failure strings. The contract schema lives at `$CLAUDE_PLUGIN_ROOT/skills/plan/references/error-contract.md`. All agents reference it via this absolute path.

### SKILL.md Size

Keep each SKILL.md under 500 lines. Move detailed reference material to `references/*.md` and link from SKILL.md. Reference links must be one level deep — no `references/sub/file.md`.

### Adding a New Skill

1. Create `skills/<name>/SKILL.md` with `name` and `description` frontmatter.
2. Add `skills/<name>/agents/<name>.md` if the skill dispatches an agent.
3. Add `skills/<name>/references/` for skill-local reference docs.
4. If the skill's agent or references are needed by other skills, move them to the plugin root.
5. Add a routing row to `agents/agentic-operations-lead.md`.
6. Add a delegation row to `skills/plan/SKILL.md`.

---

## Development Commands

All commands run from `plugins/rubysmithing/`:

```bash
bundle install              # Install dependencies

bundle exec rubocop         # Lint
bundle exec rubocop -a      # Lint with autocorrect

bundle exec rspec                              # Full test suite
bundle exec rspec spec/path/to/file_spec.rb   # Single spec

bundle exec git-lint        # Validate commit message format
```

---

## Contributing

Contributions to skills, agents, and references are welcome. Open a pull request against the `development` branch. Run `bundle exec rubocop` and `bundle exec rspec` before submitting.

## License

MIT