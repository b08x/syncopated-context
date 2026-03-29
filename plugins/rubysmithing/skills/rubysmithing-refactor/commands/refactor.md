---
description: Audit and refactor a Ruby file toward project-detected conventions (RuboCop, StandardRB, or Rubysmith defaults).
argument-hint: "<file-path>"
allowed-tools: ["Read", "Write", "Grep", "Glob", "Bash"]
---

Run a rubysmithing-refactor audit and convention pass on the target. Load and follow all instructions from:
`$CLAUDE_PLUGIN_ROOT/skills/rubysmithing-refactor/SKILL.md`

**Detect target from arguments:**

- File path → read and refactor that file
- No argument → ask: "Which file or code snippet should I refactor?"

**Follow all steps in the skill:**

1. **Detect convention target** — `.rubocop.yml` / `standard` in Gemfile / `.rubysmith` / community idioms
2. **Detect mode** — Lite (≤50 lines, simple utility) or Standard (all others)
3. **Pre-refactor audit** — output issues by severity (CRITICAL / WARNING / INFO) with line numbers and pattern keys
4. **Refactor** — apply transformations, show before/after inline for behavior-altering changes
5. **Verify Zeitwerk compliance** — module/class names match file paths
6. **Output** — complete refactored file, change log, behavioral change flags

Always audit before rewriting. Never truncate. Never silently alter behavior. Load `references/refactor-patterns.md` for the full transformation catalog.
