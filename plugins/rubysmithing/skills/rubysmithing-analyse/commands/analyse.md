---
description: Analyse Ruby code using Gemba Walk (how does this actually work), Muda waste audit (what's bloated or dead), Root-Cause Tracing (why is this failing), or Five Whys (iterative causal drilling). Auto-selects method from context.
argument-hint: "[file-path | directory | --trace | --muda | --gemba | --why]"
allowed-tools: ["Read", "Grep", "Glob"]
---

Run a rubysmithing-analyse investigation. Load and follow all instructions from:
- `$CLAUDE_PLUGIN_ROOT/skills/rubysmithing-analyse/SKILL.md`
- `$CLAUDE_PLUGIN_ROOT/skills/rubysmithing-analyse/references/analyse-methods.md` (load immediately — full method templates)

**Detect method from arguments:**

- `--trace` or `-t` → Root-Cause Tracing (backward call-chain from symptom to source)
- `--muda` or `-m` → Muda waste analysis (7 waste types mapped to Ruby artifacts)
- `--gemba` or `-g` → Gemba Walk (actual vs. assumed code behavior)
- `--why` or `-w` → Five Whys (iterative causal drilling)
- No flag → auto-select from context signals per SKILL.md method table

**Detect target from arguments:**

- File path (`.rb`, `Gemfile`, `.gemspec`) → analyse that file
- Directory path → analyse the project as a whole
- No argument → analyse Ruby files in the current working directory
- Inline pasted code or stack trace (no path) → analyse the provided content

**Convention detection (before analysis):**

Check for: `.rubocop.yml` → RuboCop | `standard` in Gemfile → StandardRB | `.rubysmith` → Rubysmith defaults | none → community idioms.

**Output format per SKILL.md:**

```
METHOD: [selected method]
TARGET: [file/directory/snippet]
CONVENTION TARGET: [detected target]

[Method findings]

ACTIONABLE NEXT STEPS:
- [Finding] → /rubysmithing:refactor [file] (pattern: [key])
- [Finding] → /rubysmithing:report --advisory
```

Execute the selected method's full workflow from `references/analyse-methods.md`. Key every finding to a named pattern from `rubysmithing-refactor/references/refactor-patterns.md` where one applies.
