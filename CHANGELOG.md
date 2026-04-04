## [unreleased]

### 🚀 Features

- *(marketplace)* Add notebook plugin with research and recall skills
- *(notebook/recall)* Add checkpoint-based session extraction with multi-platform support
- *(rubysmithing,notebook)* Add systems-observer agent and expand recall capabilities
- *(recall)* Implement normalized session extraction and unified recall workflow
- *(skills)* Add notebooklm and readme-generator skills
- *(core)* Initialize gitagent specification
- *(agents)* Add agent roles and command definitions
- *(skills)* Migrate and standardize agent skills and tools
- *(plugins)* Integrate bashsmithing and update rubysmithing

### 🐛 Bug Fixes

- *(notebook/recall)* Add missing flags to restic snapshots command

### 💼 Other

- *(dev)* Add validation scripts, tasks, and specification documents

### 🚜 Refactor

- *(skills)* Move recall skill to top-level and remove plugins/notebook

### 📚 Documentation

- Update repository documentation and marketplace manifest
- *(agnostic)* Replace specific AI agent references with agnostic terminology
- *(agnostic)* Finalize harness-agnostic terminology across plugins and skills

### ⚙️ Miscellaneous Tasks

- *(repo)* Update repository configuration and dev container
## [2.1.0] - 2026-03-30

### 🚀 Features

- Add /rubysmithing:diagnose workflow command
- Add /rubysmithing:audit workflow command
- Add /rubysmithing:translate workflow command
- Add /rubysmithing:document workflow command
- Add /rubysmithing:flow workflow command
- Add /rubysmithing:vibe workflow command with SADD tree-of-thoughts
- Add workflow command routing to orchestrator and plan SKILL.md
- Rename 13 agents to job-function names and add 6 workflow commands (v2.1.0)
- Update READMEs via readme-generator skill and sync data-engineer docs
- *(data-engineer)* Add kreuzberg document ingestion and RRF hybrid search

### 🐛 Bug Fixes

- Correct tui-engineer → ux-engineer in maintenance-architect

### 🚜 Refactor

- Rename context, scaffold, refactor agents to job-function names
- Rename genai, tui, main, yardoc agents to job-function names
- Rename analyse, deconstructor agents; fix stale cross-ref in agentic-software-engineer
- Rename judge, meta-judge, report agents to job-function names
- Rename orchestrator to agentic-operations-lead; complete agent rename

### 📚 Documentation

- Update agent names in CLAUDE.md, README files
- Restore agents/README.md rename reference table
- Update READMEs via readme-generator skill

### ⚙️ Miscellaneous Tasks

- Add .worktrees/ to .gitignore
- Update SKILL.md delegation table and bump version to 2.1.0
- Remove migration reference doc from agents/ directory
- Updated changelog
