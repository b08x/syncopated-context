---
description: Initialize a new Ruby project using rubysmith (apps/tools) or gemsmith (publishable gems).
argument-hint: [project-name] [--gem]
allowed-tools: ["Bash", "Read", "Write"]
---

Launch the rubysmithing scaffold workflow. Load and follow all instructions from:
`$CLAUDE_PLUGIN_ROOT/skills/scaffold/SKILL.md`

**Detect tool from arguments:**

- `--gem` flag → use `gemsmith`
- Any other arguments → use `rubysmith`
- No clear signal → ask: "Will this be published as a gem on rubygems.org, or is it a local Ruby app/tool?"

**Extract project name** from arguments (must be snake_case). If not provided, ask for it.

Follow all steps in the skill:

1. **Detect tool** (rubysmith vs gemsmith)
2. **Gather requirements** — match to an archetype preset from `references/scaffold-patterns.md` Section 3, propose defaults, confirm with user
3. **Construct and show the command** before executing
4. **Execute** the CLI command
5. **Display** the generated file tree
6. **Offer** optional Standard Mode convention hardening pass
7. **Output** adaptive sub-skill chain suggestions

Never run the scaffold command without first showing it to the user. Never silently modify generated files.
