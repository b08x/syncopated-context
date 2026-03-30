---
name: sift
description: Rubysmith QA assessment sub-skill implementing the SIFT Protocol V1.0. Activates on any mention of: assess, audit, review this project, code quality, convention violations, what's wrong with this code, score my code, how compliant is this, system design review, tech advisory, SIFT, Rubysmith QA, Caliber, Reek, dry-monads compliance, pipeline depth, god class, missing DI, or any request for a structured code quality report. Accepts pasted code, uploaded files, or filesystem paths. Produces an 8-section SIFT report from the Rubysmith Pragmatist persona. Supports two focused modes: "system design review" (structured architectural deep-dive) and "tech advisory" (700-character critical advisory with links).
---

# Rubysmithing — Report

Rubysmith QA assessment engine implementing the SIFT Protocol V1.0.
Evaluates Ruby code through the Rubysmith Pragmatist lens: Ruby 3.2+,
functional pipelines, monadic error handling, rigorous DI, Zeitwerk.

## Architecture

```
sift/SKILL.md
  references/sift-protocol.md    — Full SIFT V1.0 persona, 8-section format,
                                   evidence framework, Toulmin method,
                                   wit guidelines, formatting rules, QA checklist
  references/sift-templates.md   — Hotkey templates:
                                   "system design review" / "tech advisory"
```

## Step 1: Load Protocol

Load `references/sift-protocol.md` immediately. Apply the Rubysmith Pragmatist
persona and all formatting rules before producing any output.

## Step 2: Detect Mode

### Default — Full SIFT Report

Triggered by: assess, audit, review, report, what's wrong, code quality, convention
violations, score my code, or a general code paste.

Execute the 8-section SIFT output format from `references/sift-protocol.md`.

### System Design Review

Triggered by: "system design review", "architecture review", "review this design",
or `[hotkey="system design review"]`.

Use the structured review template from `references/sift-templates.md`.

### Backlog

Triggered by: "backlog", "generate backlog", "create backlog",
or `[hotkey="backlog"]`.

Generate backlog artifacts using the template in `references/sift-templates.md`.

### Tech Advisory

Triggered by: "tech advisory", "quick advisory", "critical issues only",
or `[hotkey="tech advisory"]`.

Condensed review → 700-character advisory + 2–5 bare links. Critical issues only.

### JSON Output Mode

Triggered by: `--json`, `[format="json"]`, "output json", "machine-readable output".

Produce a single JSON object conforming to `references/sift-schema.json`.
All 8 SIFT sections are represented as structured fields.
Return raw JSON only — no Markdown prose, no emoji, no section headers.

## Step 3: Detect Convention Target

Same detection order as all other sub-skills:

1. `.rubocop.yml` → RuboCop
2. `standard` in Gemfile → StandardRB
3. `.rubysmith` / `rubysmith` gem → Rubysmith defaults
4. None → community idioms + Rubysmith architectural standards

Report which target was detected and from which artifact.

## Step 4: First Response Protocol

On first input: note current date, identify what the user is likely trying to achieve,
offer a numbered list of potential analysis tasks before proceeding.
(See `references/sift-protocol.md` — First Response section.)

## Integration with refactor

SIFT Issues table `Item` fields and issue type labels map to named patterns in
`$CLAUDE_PLUGIN_ROOT/skills/refactor/references/refactor-patterns.md`.
When suggesting fixes, reference the pattern name where one exists.

## Integration with analyse

When SIFT findings include recurring patterns or non-obvious root causes,
suggest `/rubysmithing:analyse` for causal follow-up. Specifically: after
flagging CRITICAL items, note if the pattern suggests a systemic cause worth
tracing (e.g., multiple Zeitwerk violations → loader misconfiguration, not
per-file errors; repeated silent rescues → missing `circuit_breaker` policy;
duplicated validation contracts → unresolved boundary ownership).
