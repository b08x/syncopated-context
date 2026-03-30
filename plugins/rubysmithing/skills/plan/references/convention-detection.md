# Convention Detection — Canonical Reference

Single authoritative definition of the project-convention detection cascade.
All skills load this reference rather than repeating the logic inline.

Last updated: 2026-03-18

---

## Detection Cascade (Priority Order)

Scan the target project for the following signals in strict priority order.
Stop at the first match and apply that convention target for the duration of the task.

| Priority | Signal | Convention Target | How to Detect |
| :---- | :---- | :---- | :---- |
| 1 | `.rubocop.yml` present in project root | **RuboCop** | Parse enabled cops and `TargetRubyVersion`; apply those specific rules only |
| 2 | `standard` gem in `Gemfile` or `Gemfile.lock` | **StandardRB** | Use Standard's rule set; no per-cop overrides |
| 3 | `.rubysmith` config file or `rubysmith` in Gemfile | **Rubysmith defaults** | Apply Rubysmith project template conventions |
| 4 | None of the above | **Community idioms** | Apply patterns from `rubysmithing/references/conventions.md` |

---

## What to Report

When applying the cascade, always state which target was detected and from which artifact:

```
Convention target: RuboCop (.rubocop.yml detected at project root)
Convention target: StandardRB (standard gem found in Gemfile)
Convention target: Rubysmith defaults (.rubysmith config detected)
Convention target: Community idioms (no project config found — applying conventions.md)
```

---

## Scope of Application

Convention detection applies to **every code-generating and refactoring skill**:

- `rubysmithing` (hub) — generation
- `rubysmithing-genai` — AI/NLP scaffolding
- `rubysmithing-tui` — TUI scaffolding
- `rubysmithing-refactor` — targeted refactoring
- `rubysmithing-yardoc` — documentation style and type annotation conventions

Convention detection does **not** apply to:

- `rubysmithing-context` — gem API resolution only, no code generation
- `rubysmithing-report` — QA assessment; detects convention target for reporting purposes only

---

## Lite Mode Override

In Lite Mode, convention detection still runs but its output is limited:

- Apply style rules (naming, indentation, guard clauses, frozen string literal)
- Do **not** enforce architectural mandates (async, circuit breakers, journald-logger)
- Note: `"Lite Mode applied — convention target: [target]; architectural mandates omitted"`

See `rubysmithing/SKILL.md` for Lite Mode trigger conditions.
