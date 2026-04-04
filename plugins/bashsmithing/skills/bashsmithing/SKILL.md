---
name: bashsmithing
description: Convention-aware Bash code generator for production-grade scripting (set -euo pipefail, namespaced functions, shellcheck, bats, jq, logger). Use for generating executable scripts, library functions, config wiring, data pipelines, and BATS tests. Applies project-detected conventions (Shellcheck, BATS, or community idioms) automatically. For single-file output under ~50 lines or pure standalone work, activates Lite Mode — no namespacing mandates, no Return monads, and simplified conventions. Multi-file scaffold requests always use Standard Mode regardless of per-file line count. Does NOT handle: Ruby code (rubysmithing), Python code, or TUI interfaces beyond simple output.
---

# Bashsmithing

Convention-aware Bash code generator. Generates complete, idiomatic Bash files
calibrated to project-detected conventions and task scope.

## Step 1: Detect Mode

### Lite Mode (single-file output ≤ ~50 lines, or explicitly simple tasks)

Triggers: "quick script", "simple utility", "one-off", "no dependencies", "pure bash",
or a clearly small self-contained task.

**Multi-file scaffold requests always trigger Standard Mode** regardless of individual
file line count. If the task would produce more than one file, apply Standard Mode.

In Lite Mode:

- Generate pure Bash using builtins and common utilities (e.g., `awk`, `sed`)
- No `Namespace::` namespacing mandates
- No `Return::success`/`Return::failure` monads
- Shebang and `set -euo pipefail` are still recommended but not strictly enforced
- Output a single file with a brief inline comment explaining any non-obvious choice

### Standard Mode (default for all other tasks)

Apply full conventions from `references/conventions.md`.

## Step 2: Detect Convention Target

See `references/convention-detection.md` for the canonical detection cascade.
Summary:

1. `.shellcheckrc` present → Shellcheck enforced
2. `bats/` directory present → BATS testing enforced
3. `lib/monad.sh` present → Return monads enforced
4. None → apply community idioms from `references/conventions.md`

Always state which target was detected and from which artifact before generating.

## Step 3: Architecture Context Check

Before writing any code:

- Note whether it belongs in `bin/` (entry point), `lib/` (namespaced library),
  or `settings/` (configuration).
- If `lib/monad.sh` is present, use `Return::success` and `Return::failure`
  monads for all function exits.
- If JSON validation is required, use `jq` schemas.

## Step 4: Generate

Generate complete files. No truncation. No `# ... rest of implementation` stubs.

### Standard Mode conventions — always apply

```bash
#!/usr/bin/env bash
# shellcheck shell=bash

set -euo pipefail
IFS=$'\n\t'
```

- Two-space indent, no tabs
- Use `local` for **all** variables inside functions
- Namespaced functions: `Namespace::function_name()`
- Guard clauses over nested conditionals
- Structured logging via `logger` or consistent `[INFO]`/`[ERROR]` prefixes
- Subshell wrapping `( )` for environment-altering commands (e.g., `cd`)
- Quotes around all variable expansions: `"$var"`
- Parameter expansion safety: `"${var:-default}"`

## Output Format

1. **File path** — relative to project root
2. **Complete file content**
3. **Rationale** — one sentence for non-obvious decisions only
4. **Dependency notes** — (e.g., `jq`, `bats`, `shellcheck`)
5. **Mode applied** — "Lite Mode" or "Standard Mode [convention target]"
