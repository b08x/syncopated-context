## [2.1.0] - 2026-03-29

### 🚀 Features

- Add /rubysmithing:diagnose workflow command
- Add /rubysmithing:audit workflow command
- Add /rubysmithing:translate workflow command
- Add /rubysmithing:document workflow command
- Add /rubysmithing:flow workflow command
- Add /rubysmithing:vibe workflow command with SADD tree-of-thoughts
- Add workflow command routing to orchestrator and plan SKILL.md
- Rename 13 agents to job-function names and add 6 workflow commands (v2.1.0)

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

### ⚙️ Miscellaneous Tasks

- Add .worktrees/ to .gitignore
- Update SKILL.md delegation table and bump version to 2.1.0
- Remove migration reference doc from agents/ directory
