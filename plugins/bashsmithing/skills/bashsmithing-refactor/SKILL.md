---
name: bashsmithing-refactor
description: Convention-targeted Bash refactoring sub-skill. Activates on any mention of: refactor, clean up, fix conventions, this script is messy, help me improve this, bash anti-patterns, shellcheck violations, shellcheck warnings, SC codes, make this idiomatic, add error handling, set -e, set -o pipefail, quote variables, local variables, fix function names, or missing exit codes. Accepts pasted snippets, uploaded scripts, or filesystem paths. Detects convention target from project config (Shellcheck, EditorConfig) before applying changes. Produces pre-refactor audit + complete refactored script + change log. Applies Lite Mode bypass for scripts under ~50 lines where architectural mandates would be disproportionate.
---

# Bashsmithing — Refactor

Targeted refactoring of existing Bash code toward project-detected conventions.
Always audits before rewriting. Never silently drops functionality.

## Inputs Accepted

- Pasted snippet — inline code in the conversation
- Uploaded script — from `/mnt/user-data/uploads/`
- Filesystem path — via bash tools
- Multiple scripts — process in dependency order (libraries/includes first)

**Compound prompts** (e.g., "refactor this backup script AND build a cron task for it"):
Handle the refactoring component here. State:
"Handling refactor. Cron configuration should be addressed with separate bash tools."

## Step 1: Detect Convention Target

Priority order:
1. `.shellcheckrc` → Shellcheck (parse excluded codes, target shell version)
2. `.editorconfig` → EditorConfig (indentation, line endings)
3. `.bashsmith` / `bashsmith` project → Bashsmith defaults
4. None → community idioms from `references/refactor-patterns.md`

## Step 2: Detect Mode

### Lite Mode
Apply when: script is ≤ ~50 lines, or request is clearly a simple one-off utility.

Lite Mode refactor scope:
- Style fixes only (quoting, indentation, naming, SC2086)
- Do NOT add complex logging frameworks or namespaced libraries
- Do NOT mandate external constant files for a simple script
- Note: "Lite Mode applied — architectural mandates omitted (disproportionate for scope)"

### Standard Mode
Apply for all other inputs. Full pattern catalog from `references/refactor-patterns.md`.

## Step 3: Pre-Refactor Audit

Before rewriting, output a brief audit:

```
FILE: bin/deploy.sh
Convention target: Shellcheck (.shellcheckrc detected)
Mode: Standard

CRITICAL
  [line 3]  Missing pipefail — pipes can fail silently  [missing_pipefail]
  [line 1]  Missing errexit — script continues on error [missing_errexit]
ERROR
  [line 12] Unquoted variable "$file"                   [unquoted_variables]
  [line 45] Global variable leak in update_status()     [missing_local]
WARNING
  [line 8]  CamelCase function name ProcessData         [function_name_case]
  [line 22] Hardcoded path /usr/local/bin/curl          [hardcoded_paths]
INFO
  [line 1]  Unused variable TEMP_DIR                    [unused_variables]
```

Pattern names in brackets map to `references/refactor-patterns.md`.

## Step 4: Refactor

Apply changes. For each non-trivial transformation:
- Show before/after inline for any change that alters behavior
- Add inline comment if refactored pattern is non-obvious
- Flag explicitly if a change alters observable behavior (e.g., adding `set -e`)

## Step 5: Verify Shellcheck Compliance

Confirm post-refactor:
- Shellcheck runs clean on the refactored script
- All CRITICAL and ERROR issues resolved
- Indentation matches `.editorconfig` if present

## Output Format

1. Pre-refactor audit (issues, severity, pattern key)
2. Complete refactored script — always full file, never diff-only
3. Change log — bullet list of what changed and why
4. Behavioral changes — flagged explicitly if any (e.g., "Script now exits on command failure")
5. Mode applied — Lite or Standard + convention target
