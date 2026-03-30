---
description: Run a SIFT Protocol V1.0 QA assessment on a Ruby file, directory, or pasted code snippet.
argument-hint: [file-path | directory | --advisory | --design]
allowed-tools: ["Read", "Grep", "Glob"]
---

Run a rubysmithing-report SIFT Protocol assessment. Load and follow all instructions from:
- `$CLAUDE_PLUGIN_ROOT/skills/sift/SKILL.md`
- `$CLAUDE_PLUGIN_ROOT/skills/sift/references/sift-protocol.md` (load immediately — Rubysmith Pragmatist persona)

**Detect mode from arguments:**

- `--advisory` or `-a` → Tech Advisory mode (700-char condensed, critical issues only)
- `--design` or `-d` → System Design Review mode (structured architectural deep-dive)
- No flag → Full SIFT Report (8-section format)

**Detect target from arguments:**

- File path (`.rb` file) → assess that file
- Directory path → glob for `**/*.rb`, assess the project as a whole
- No argument → assess Ruby files in the current working directory
- Inline pasted code (no path) → assess the provided snippet

**Convention detection (before assessment):**

Check for: `.rubocop.yml` → RuboCop | `standard` in Gemfile → StandardRB | `.rubysmith` → Rubysmith defaults | none → community idioms + Rubysmith architectural standards.

**First Response Protocol:**

Note current date, identify what the user is trying to achieve, offer a numbered list of potential analysis tasks before proceeding.

Execute the selected mode's output format per `references/sift-protocol.md`. When suggesting fixes, reference named patterns from `$CLAUDE_PLUGIN_ROOT/skills/refactor/references/refactor-patterns.md`.
