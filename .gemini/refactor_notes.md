# Refactor Notes: Plugin Architecture to Hermes-Compatible Modular Structure

## Objective
Transition away from the `plugins/` architecture towards a unified structure of `skills/`, `commands/`, `tasks/`, `workflows/`, and `agents/` grouped by **Concepts** (identified via `graphify`) to ensure compatibility with **Hermes Agent** and general modularity.

## Conceptual Redistribution Plan (Core Pillars)

### 1. Operations & Leadership
- **Agents**: `ruby-operations-lead`, `ruby-diagnostics-engineer`
- **Skills**: `bashsmithing-report`, `rubysmithing-analyse`
- **Workflows**: `diagnose.md`, `flow.md`
- **Rationale**: Focuses on the "Run" and "Audit" aspects of the lifecycle.

### 2. Architecture & Design
- **Agents**: `ruby-backend-architect`, `ruby-cognitive-architect`, `ruby-maintenance-architect`
- **Skills**: `rubysmithing-plan`, `bashsmithing-scaffold`, `rubysmithing-scaffold`
- **Workflows**: `vibe.md`, `schema.md`
- **Rationale**: High-level structure and project bootstrapping.

### 3. Risk & Compliance
- **Agents**: `ruby-director-ai-risk`, `ruby-compliance-guardrail`
- **Skills**: `rubysmithing-sift`, `bashsmithing-report` (Compliance mode)
- **Workflows**: `audit.md`
- **Rationale**: Safety, security, and protocol enforcement (SIFT/Toulmin).

### 4. Context & Knowledge Engineering (Recall Refactor)
- **Agents**: `ruby-context-engineer`, `ruby-data-engineer`
- **Skills**: `rubysmithing-context`, `bashsmithing-context`, `recall`
- **Workflows**: `translate.md`
- **Refined Backlog (Hermes/Modular Focus)**:
    - **P0: PII/Secrets Scrubber**: Automated scrubbing in the extraction pipeline (Issue #30).
    - **P1: UV Project Refactor**: Professionalize Python packaging for `recall` (pyproject.toml, dependency management).
    - **P1: Gemini CLI Export**: Replace raw scraping with official `gemini export` commands (Issue #34).
    - **P1: Unified DateTime**: Enforce a unified value object for temporal logic (Issue #35).
    - **P1: Restic Integration**: Analyze file changes from restic backups for work session context.
    - **P1: Chunking Strategies**: Handle large session JSON files efficiently (Memory/Context management).
    - **P2: Obsidian Integration**: Correlate AI sessions with Obsidian vault notes (Issue #26).
    - **P3: NotebookLM Sources**: Extract sources/citations (Modified from full indexing).
- **Dropped Items (Out of Scope)**:
    - Dedicated Graph Database (use existing RAG/Graphify instead).
    - Web/Shell History (High PII noise/risk).
    - Visual Dashboards (Not relevant for CLI-first engineering agent).

### 5. Engineering & Development Experience
- **Agents**: `ruby-software-engineer`, `ruby-platform-engineer`, `ruby-developer-experience`, `ruby-ux-engineer`
- **Skills**: `rubysmithing-refactor`, `bashsmithing-refactor`, `bashsmithing-tui`, `rubysmithing-tui`
- **Workflows**: `document.md`
- **Rationale**: Hands-on code modification, UI/UX, and local DX.

## Path Mapping (Filesystem View)

| Concept Node | New Agent Path | New Skill Path | New Workflow Path |
| :--- | :--- | :--- | :--- |
| **Ops & Lead** | `agents/ops/` | `skills/ops/` | `workflows/ops/` |
| **Architecture** | `agents/arch/` | `skills/arch/` | `workflows/arch/` |
| **Compliance** | `agents/risk/` | `skills/risk/` | `workflows/risk/` |
| **Knowledge** | `agents/knowledge/` | `skills/knowledge/` | `workflows/knowledge/` |
| **Engineering**| `agents/eng/` | `skills/eng/` | `workflows/eng/` |

## Technical Implementation (Hermes Transition)

### 1. Command Migration (Markdown Conversion)
- Existing `.toml` commands in `commands/gemini/` move to `commands/[concept]/[name].md`.
- **Transformation Example**: `commands/gemini/ruby/nlp.toml` → `commands/knowledge/nlp.md`.
- Each new Markdown command will include a `## Hermes Config` block with `toolsets: [terminal, file]` etc.

### 2. Path Resolution (Universal & Portable)
- **Eliminate `git` dependency**: Avoid `git rev-parse` as scripts may run outside a repo.
- **Bash Implementation**:
  ```bash
  # In settings/main.sh or bootstrap.sh
  export SYNC_CONTEXT_ROOT="${SYNC_CONTEXT_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
  export SYNC_LIB_DIR="${SYNC_LIB_DIR:-${SYNC_CONTEXT_ROOT}/lib}"
  ```
- **Ruby Implementation**:
  ```ruby
  # In core library files
  SYNC_CONTEXT_ROOT = ENV.fetch('SYNC_CONTEXT_ROOT', File.expand_path('..', __dir__))
  ```
- **Rationale**: Relying on `${BASH_SOURCE[0]}` ensures that no matter where the script is called from, it can find its sibling `lib/` and `settings/` directories relative to its own location. The environment variable override allows for "global" installations.

### 3. Task Mapping
- Task definitions from `plugins/rubysmithing/tasks/` move to `tasks/[concept]/[name]/`.
- Rationale: High-level concepts allow Hermes to find the right sub-agent by *intent* (e.g., "Review architectural safety" -> `agents/risk/`) rather than by tool.

## Findings Recap
- **Orchestration**: Hermes relies on explicit `delegate_task`.
- **Conceptual Shift**: `graphify` confirms that our smithing tools are not framework silos but shared concepts of Architecture, Compliance, and Knowledge.
- **De-risking**: Issue #31 (Path Resolution) is solved by absolute project-anchored paths.
