---
name: scaffold
description: "Ruby project scaffolder using rubysmith (apps, tools, scripts) or gemsmith (publishable gems). Activates on any mention of: scaffold a project, scaffold a gem, new ruby project, new gem, create gem, bootstrap project, rubysmith, gemsmith, generate project skeleton, project template, set up a new ruby app, start a ruby tool, start a ruby script, create a new gem for rubygems, initialize ruby project, rubysmith build, gemsmith build, new ruby app, create a ruby tool. Runs rubysmith for local Ruby tools and apps; runs gemsmith for gems intended for rubygems.org. Executes the CLI, displays generated file tree, then optionally applies Standard Mode convention hardening. After scaffolding, suggests and chains to tui, genai, yardoc, and context. Use whenever a user wants to start a new Ruby project from scratch."
---

# Rubysmithing — Scaffold

Project initializer for the Ruby terminal-native stack. Runs `rubysmith` or `gemsmith`
CLI directly, then optionally hardens the generated project with Standard Mode conventions.

## Companion Skills

| Skill | When |
|:------|:-----|
| `context` | Before any post-scaffold library-specific code generation |
| `tui` | Project needs a terminal UI layer |
| `genai` | Project needs LLM, RAG, or MCP components |
| `refactor` | Convention hardening deferred or deeper cleanup needed |
| `yardoc` | YARD documentation for scaffolded files |

---

## Step 1: Detect Tool

Use this decision table to select `rubysmith` or `gemsmith`:

| Signal in user request | Tool |
|------------------------|------|
| "publishable gem", "rubygems.org", "gemspec", "gemsmith", "gem release" | `gemsmith` |
| "app", "tool", "script", "utility", "project", "local", "rubysmith" | `rubysmith` |
| Ambiguous | Ask exactly: "Will this be published as a gem on rubygems.org, or is it a local Ruby app/tool?" |

See `references/scaffold-patterns.md` Section 4 for the full decision tree and secondary signal table.

---

## Step 2: Gather Requirements

Collect: **project name** (must be snake_case) and **feature flags**.

Rather than asking about each flag individually, match the project to an archetype from
`references/scaffold-patterns.md` Section 3 and propose the preset. Ask the user to
confirm or adjust.

**rubysmith defaults** (for most projects): `--git --rake --console --rspec --readme`
Ask specifically about: Docker, GitHub CI, license, citation.

**gemsmith defaults** (for most gems): `--rspec --zeitwerk --github`
Ask specifically about: CLI entry point (`--cli`), security signing (`--security`), CircleCI.

**gemsmith config warning**: gemsmith requires `~/.config/gemsmith/configuration.yml`
with author info — it will error without it. Remind the user: run `gemsmith --edit`
to generate the config before proceeding if they haven't already.

---

## Step 3: Construct & Show Command

Assemble the command and show it before executing:

```
Tool:    rubysmith
Project: my_tool
Flags:   --git --rake --rspec --readme
Command: rubysmith build my_tool --git --rake --rspec --readme
```

State which config file will be read (`~/.config/rubysmith/configuration.yml` or
`~/.config/gemsmith/configuration.yml`).

---

## Step 4: Execute

```bash
rubysmith build <name> [flags]
# or
gemsmith build --name <name> [flags]
```

**On non-zero exit:** show the error verbatim. Diagnose the common causes:

- Missing config → run `rubysmith --edit` or `gemsmith --edit`
- Name collision → directory already exists; choose a different name or remove it
- Tool not installed → `gem install rubysmith` or `gem install gemsmith`

Do not proceed to Step 5 on error.

**On success:** display the generated file tree:

```bash
find <name> -type f | sort
```

Reference `references/scaffold-patterns.md` Section 7 for annotated tree examples
if the live output needs supplemental context.

**Note:** context is NOT needed for this step. The scaffold CLI invokes
build toolchain gems, not runtime library APIs. Activate context when
writing post-scaffold code that touches runtime gems.

---

## Step 5: Optional Convention Pass

Ask:

```
Scaffold complete. Apply Standard Mode convention hardening? (y/n)

This will add:
  - # frozen_string_literal: true to all .rb files
  - Zeitwerk loader wiring in the boot file
  - journald-logger replacing any puts/p calls
  - Async fiber boot pattern (if network I/O detected in Gemfile)
  - circuit_breaker stubs for external API calls (if detected)

Answer n to skip — run refactor on this project whenever ready.
```

**If `y`:** Apply each transformation from `references/scaffold-patterns.md` Section 6.
Generate modified files completely — no diffs, no stubs. Output a change log in the
format shown in Section 6.

**If `n`:** Skip. Note: "Convention pass skipped. Run `refactor` when ready."

**Batch/non-interactive context:** default to `n`. Never silently modify files.

---

## Step 6: Sub-Skill Chain Suggestions

After the scaffold (and optional convention pass), output an adaptive routing block.
Tailor it — suppress suggestions that are already covered by the scaffold flags used:

```
Next steps — route to these skills as needed:

  context  → verify gem APIs before writing library-specific code
  tui      → add a terminal UI layer
  genai    → add LLM, RAG, or MCP components
  yardoc   → generate YARD documentation for scaffolded files
  refactor → apply convention hardening (if skipped above)
```

**Adaptive suppression rules:**

- `--cli` was passed to gemsmith → suppress `tui` suggestion
- Project name contains "llm", "rag", "ai", "gpt", "chat", "embed" → promote `genai` to top
- Convention pass was applied → remove `refactor` from list

---

## Output Format

1. **Tool selected** + command executed
2. **Generated file tree** (from `find` or Section 7 reference)
3. **Convention pass result** — applied (with change log) or skipped
4. **Gemfile additions** required (if convention pass ran)
5. **Sub-skill chain suggestions** (adaptive)
