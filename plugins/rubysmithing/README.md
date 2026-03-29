<div align="center">

# rubysmithing plugin

Contributor reference for the rubysmithing Claude Code plugin — skill structure, authoring conventions, and development workflow.

</div>

---

## Plugin Structure

The plugin follows a **shared-root pattern**: resources used by multiple skills live at the plugin root; skill directories contain only what is exclusive to that skill.

```
plugins/rubysmithing/
├── .claude-plugin/plugin.json   # Plugin metadata (name, version, description)
├── agents/                      # Shared agents — referenced as $CLAUDE_PLUGIN_ROOT/agents/
│   ├── rubysmithing-context.md  # Gem API verification prerequisite
│   ├── rubysmithing-genai.md    # AI/NLP scaffolder
│   └── rubysmithing-tui.md      # TUI scaffolder
├── commands/                    # Shared commands — context cache management
├── references/                  # Shared reference docs
│   ├── gem-registry.md          # Context7 ID → gem mapping with architectural roles
│   ├── cache-cli.md             # context_cache.rb CLI reference
│   ├── genai-patterns.md        # Verified AI/NLP implementation patterns
│   ├── design-patterns.md       # TUI layout paradigms and design system
│   └── tui-patterns.md          # Bubble ecosystem component patterns
├── scripts/
│   └── context_cache.rb         # SQLite-backed gem API cache CLI
├── assets/
│   └── skeleton/                # TUI project skeleton (copied per scaffold)
├── skills/
│   ├── plan/                    # Hub orchestrator; holds error-contract.md + conventions
│   ├── analyse/                 # Gemba Walk, Muda, Root-Cause Tracing, Five Whys
│   ├── context/                 # SKILL.md only — content at plugin root
│   ├── genai/                   # SKILL.md only — content at plugin root
│   ├── refactor/                # Convention-targeted rewrites
│   ├── scaffold/                # rubysmith / gemsmith project initialization
│   ├── sift/                    # SIFT Protocol QA audits
│   ├── tui/                     # SKILL.md only — content at plugin root
│   └── yardoc/                  # YARD documentation generator
├── Gemfile                      # Dev/test dependencies
├── .rubocop.yml                 # RuboCop config (Ruby 3.4)
└── .tool-versions               # Ruby 3.4.4 via asdf
```

---

## Development Commands

All commands run from `plugins/rubysmithing/`:

```bash
bundle install          # Install dependencies

bundle exec rubocop     # Lint
bundle exec rubocop -a  # Lint with autocorrect

bundle exec rspec                              # Full test suite
bundle exec rspec spec/path/to/file_spec.rb   # Single spec

bundle exec git-lint    # Validate commit message format
```

---

## Skill Authoring

### SKILL.md Frontmatter

Only two fields are supported:

```yaml
---
name: skill-name          # ≤64 characters
description: Third-person description of what the skill does and when to activate it.  # ≤1024 characters
---
```

No other frontmatter fields. Description must be written in third person — it is injected into Claude's system prompt and point-of-view consistency matters for reliable activation.

### Shared vs Skill-Local Resources

**Shared (plugin root):** Use for resources referenced by two or more skills. Reference via absolute path:

```
$CLAUDE_PLUGIN_ROOT/references/gem-registry.md
$CLAUDE_PLUGIN_ROOT/scripts/context_cache.rb
$CLAUDE_PLUGIN_ROOT/agents/rubysmithing-context.md
```

**Skill-local (inside `skills/<name>/`):** Use for resources exclusive to one skill. Reference via relative path from SKILL.md:

```
references/refactor-patterns.md
agents/rubysmithing-refactor.md
```

Never mix: a relative path from `skills/genai/SKILL.md` that says `references/foo.md` resolves to `skills/genai/references/foo.md`, not the plugin root.

### SKILL.md Size

Keep each SKILL.md under 500 lines. Move detailed reference material to `references/*.md` and link from SKILL.md. Reference links must be one level deep — no `references/sub/file.md`.

### Adding a New Skill

1. Create `skills/<name>/SKILL.md` with `name` and `description` frontmatter.
2. Add `skills/<name>/agents/<name>.md` if the skill dispatches an agent.
3. Add `skills/<name>/references/` for skill-local reference docs.
4. If the new skill's agent or references are needed by other skills, move them to the plugin root instead.
5. Update `$CLAUDE_PLUGIN_ROOT/skills/plan/agents/rubysmithing-orchestrator.md` routing table to include the new skill.

### Error Contract

Sub-agents return structured `[AGENT ERROR]` blocks rather than bare failure strings. The contract schema lives at `skills/plan/references/error-contract.md`. All agents reference it via `$CLAUDE_PLUGIN_ROOT/skills/plan/references/error-contract.md`.

---

## Convention Modes

### Lite Mode
Single-file output ≤~50 lines, stdlib only. No `dry-schema`, `async`, `circuit_breaker`. The `frozen_string_literal` comment is recommended but not enforced.

### Standard Mode
All other tasks. Full conventions required:

- `# frozen_string_literal: true` as the first line of every file
- Zeitwerk-compliant path ↔ class name mapping
- `journald-logger` not `puts`
- `Async { }` not `Thread.new`
- `circuit_breaker` wrapping on external API calls
- `module_function` not `extend self`

Multi-file scaffold requests always trigger Standard Mode regardless of individual file line counts.

---

## Gem API Cache

The `context_cache.rb` script manages a SQLite database at `~/.rubysmithing/context_cache.db`. It is the shared prerequisite for all library-specific code generation.

```bash
# Check cache status for a gem
ruby scripts/context_cache.rb fetch ruby_llm --json

# Manually store a resolved entry
ruby scripts/context_cache.rb store ruby_llm /crmne/ruby_llm '[".chat(...)"]' 'RubyLLM.chat'

# List all cached gems
ruby scripts/context_cache.rb list

# Force a fresh lookup
ruby scripts/context_cache.rb evict ruby_llm
```

See `references/cache-cli.md` for full exit codes and `--json` output shapes. See `references/gem-registry.md` for the curated Context7 ID mapping covering ~40 gems in the stack.
