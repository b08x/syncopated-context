---
name: setup-memory
description: Help users build their CLAUDE.md file and configure memory system for optimal Claude Code experience.
license: MIT
allowed-tools: Read Edit Grep Glob Bash Write
metadata:
  author: b08x
  version: "1.0.0"
  category: automation
---

# Setup Memory

Help the user build their CLAUDE.md file.

## Process

1. **Ask these questions:**

   - What do you do? (job, role, main activity)
   - What are you working on? (main projects)
   - How do you prefer to communicate? (formal/casual, brief/detailed)
   - Any preferences for how I should work?

2. **Generate CLAUDE.md:**

```markdown
# About Me

[Their role/activity]

## Current Focus

[Their projects]

## Communication Style

[Their preferences]

## How to Work With Me

[Their working preferences]

## This Vault

in addition to being an "obsidian vault", this folder also functions
as an instance of jekyll...

_drafts/
_notes/
assets/
      /img
      /audio
      /video
      /pdf
      /gz|iso|otherfiles
Archive/
Bases/
Daily/
Dashboards/
Projects/
NotebookLM/
Research/
Templates/
```

3. **Write to CLAUDE.md**

4. **Confirm:** "Your memory is set up! I'll read this every session."
