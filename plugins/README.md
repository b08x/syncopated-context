# syncopated-context plugins

Plugin ecosystem for Claude Code featuring specialized development and productivity tools.

---

## Available Plugins

### rubysmithing
**Convention-aware Ruby development suite**

Thirteen specialized agents handle Ruby code generation, TUI scaffolding, AI/NLP integration, refactoring, QA auditing, and documentation. Adaptive convention detection with Lite/Standard mode switching based on project complexity.

- **Version**: 2.1.0
- **Category**: Development
- **Key Skills**: `plan`, `analyse`, `genai`, `tui`, `sift`, `scaffold`, `yardoc`
- **Architecture**: Shared-root pattern with hub-and-spoke delegation

### notebook
**Multi-platform AI session recall and analysis**

Comprehensive session aggregation across Claude Code, Hermes, Gemini CLI, and OpenCode with GitHub commit correlation and restic backup diff analysis. Temporal correlation engine with cross-platform synthesis and actionable next steps.

- **Version**: 2.0.0
- **Category**: Productivity
- **Key Skills**: `recall`, `notebooklm`, `query`
- **Integration**: GitHub CLI, restic backups, NotebookLM document processing

---

## In Development

### bashsmithing
**Convention-aware Bash development suite**

Shellcheck integration, BATS testing framework, and TUI scaffolding using the Gum/Charm ecosystem. Pattern matching for common Bash antipatterns with automated fixes.

### fedora
**Fedora ecosystem tooling**

- **fedora:workstation** — Desktop environment configuration and package management
- **fedora:server** — Server deployment and configuration management
- **fedora:packaging** — RPM packaging workflows and spec file generation

### linux
**Linux system administration**

- **linux:audio** — JACK, ALSA, PulseAudio, PipeWire configuration
  - **linux:audio:jack** — Real-time audio setup and routing
  - **linux:audio:alsa** — Hardware-level audio configuration
  - **linux:audio:pulse** — Desktop audio management
  - **linux:audio:pipewire** — Modern audio server configuration

### kb (knowledge base)
**Research and documentation workflows**

- **kb:generate** — Automated documentation generation from source
- **kb:edit** — Collaborative editing workflows with version control
- **kb:research** — Information gathering and synthesis pipelines

### devops
**Infrastructure and deployment automation**

- **devops:ansible** — Playbook generation and inventory management
- **devops:containers** — Docker/Podman workflows and Kubernetes manifests
- **devops:tooling** — CI/CD pipeline configuration and monitoring setup

### genai
**Generative AI and NLP tooling**

- **genai:rag** — Retrieval-augmented generation pipelines
- **genai:nlp** — Natural language processing workflows
- **genai:persona** — AI persona development and training

### nlp
**Advanced natural language processing**

- **nlp:sfl** — Semantic feature learning and extraction
- **nlp:persona_development** — Conversational AI personality training

---

## Installation

Install the entire plugin suite:

```bash
claude plugin add syncopated-context
```

Or install individual plugins:

```bash
claude plugin add syncopated-context/rubysmithing
claude plugin add syncopated-context/notebook
```

---

## Architecture Patterns

### Shared-Root Pattern (rubysmithing)

Agents, references, and scripts live at plugin root; skills reference via `$CLAUDE_PLUGIN_ROOT/`. Eliminates duplication while maintaining skill modularity.

### Multi-Platform Extraction (notebook)

Platform-specific extractors with unified correlation engine. Temporal timeline synthesis across session sources with external data integration.

### Convention Detection (bashsmithing, rubysmithing)

Adaptive convention recognition from project configuration files with fallback to community idioms. Mode switching based on complexity heuristics.

---

## Contributing

Each plugin maintains its own development workflow and testing requirements. See individual plugin directories for specific contribution guidelines.

## License

[MIT](../LICENSE) — Robert Pannick