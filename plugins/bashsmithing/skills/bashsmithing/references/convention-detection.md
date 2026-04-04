# Bashsmithing Convention Detection

The following cascade is used to detect project-specific conventions. When
multiple indicators are present, the highest priority (first matching rule)
governs the output.

## Detection Cascade

| Priority | Indicator | Convention Enforced |
| :--- | :--- | :--- |
| 1 | `.shellcheckrc` present | **Shellcheck Enforcement**: Code must be strictly Shellcheck-clean according to the project's rules. |
| 2 | `bats/` directory exists | **BATS Testing**: All logic should be broken into testable functions with BATS test files in `bats/`. |
| 3 | `lib/monad.sh` present | **Monadic Returns**: Use `Return::success` and `Return::failure` from the project's library. |
| 4 | `bin/`, `lib/`, `settings/` | **Directory-Driven Standard Mode**: Follow namespacing and directory structure mandates. |
| 5 | None of the above | **Default Community Mode**: Apply base `conventions.md` defaults (set -euo pipefail, local, quotes). |

## Reporting Detection

Before generating code, state which conventions were detected:

> **Detected Conventions:**
> - **Source**: `.shellcheckrc` + `lib/monad.sh`
> - **Mode**: Standard Mode (Shellcheck + Monads)

## Directory Structure Enforcement

If `bin/`, `lib/`, and `settings/` directories exist, `bashsmithing` will automatically
place generated files in their respective locations:

- **Entry points**: `bin/` (executables)
- **Functions/Libraries**: `lib/` (namespaced)
- **Configuration**: `settings/` (defaults/wiring)
