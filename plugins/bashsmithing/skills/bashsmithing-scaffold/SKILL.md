---
name: bashsmithing-scaffold
description: New Bash project bootstrapper. Use this skill whenever someone wants to create a new shell-based project, start a new bash script project from scratch, bootstrap bash tooling, or set up a fresh project directory with bashsmithing conventions. Trigger on phrases like "new bash project", "scaffold a project", "create a shell project", "bootstrap a bash tool", "set up a new script project", "start a new bash script", "create a new tool in bash", or "initialize a bash project". Always use this skill when the intent is to create a full project structure — not just write a single script.
---

# Bashsmithing Scaffold

Bootstraps a new Bash project with bashsmithing conventions: strict mode, JSON monads,
robust environment bootstrapping, shellcheck + BATS quality gates, and optional gum TUI.

## Modes

**Minimal** — Pure bash, no external TUI dependency:
- `bin/setup` — robust environment/dependency setup (static asset)
- `bin/qa` — shellcheck + BATS quality gate (static asset)
- `lib/bootstrap.sh` — robust system/dep detection logic (static asset)
- `lib/monad.sh` — JSON return monad (static asset)
- `lib/cli.sh` — basic CLI option processor (static asset)
- `settings/main.sh` — strict mode bootstrap (static asset)
- `.shellcheckrc` — lint config (static asset)
- `bats/` — empty test directory, ready for tests
- `bin/run` — simple argument-driven entry point (**generated** with namespace)

**Full (TUI)** — Adds gum-based interactive menu:
- Everything in Minimal, plus:
- `lib/gum.sh` — gum TUI adapter (static asset)
- `bin/run` upgraded to an interactive gum menu (**generated** with namespace)

After scaffolding, suggest `bashsmithing-tui` to the user if they want to expand the TUI menu with additional screens or workflows.

---

## Workflow

### Step 1 — Gather project info

Extract from user context, or ask if any are missing:

| Field | Description | Default |
|:------|:------------|:--------|
| Project name | kebab-case identifier, e.g. `my-tool` | required |
| Namespace | PascalCase, e.g. `MyTool` | auto-derived (see below) |
| Output directory | where to create the project | `./<project-name>` |
| Mode | `minimal` or `full` | ask the user |

**Namespace derivation:** Split on `-`, capitalize each segment, join.
Examples: `my-tool` → `MyTool`, `git-sync-helper` → `GitSyncHelper`.

Present the derived namespace to the user and confirm before proceeding.

### Step 2 — Run scaffold.sh

Run the scaffold script to create the directory structure and copy static assets.
The script lives at `skills/bashsmithing-scaffold/scripts/scaffold.sh` relative to this repo.

```bash
bash skills/bashsmithing-scaffold/scripts/scaffold.sh \
  --name      "<project-name>" \
  --namespace "<Namespace>" \
  --output    "<output-dir>" \
  --mode      "<minimal|full>"
```

The script prints `PROJECT_NAME`, `NAMESPACE`, `OUTPUT_DIR`, and `MODE` lines to stdout.
Capture and verify these before generating files in Step 3.

### Step 3 — Generate project-specific files

Write these three files using the templates in this document, substituting
`PROJECT_NAME` and `NAMESPACE` throughout:

1. `<output-dir>/bin/run` — entry point (template depends on mode, see below)
2. `<output-dir>/bats/<project-name>_test.bats` — test skeleton
3. `<output-dir>/README.md` — minimal project README

Make `bin/run` executable after writing:
```bash
chmod +x <output-dir>/bin/run
```

### Step 4 — Confirm and summarize

Show the user the resulting file tree and print:
- Setup: `cd <output-dir> && ./bin/setup`
- Launch: `./bin/run`
- Quality gate: `./bin/qa`
- Debug trace: `BASHSMITH_DEBUG=1 ./bin/run`
- Full mode only: "Requires `gum` — install with `brew install charmbracelet/tap/gum`"
- Suggest: "To expand the TUI menu, invoke `bashsmithing-tui`."

---

## Templates

Substitute `PROJECT_NAME` (display name, e.g. `My Tool`) and `NAMESPACE`
(PascalCase, e.g. `MyTool`) at every occurrence.

---

### bin/run — Minimal mode

```bash
#!/usr/bin/env bash
# bin/run — PROJECT_NAME entry point.
# Usage: ./bin/run [--help]

source "$(dirname "${BASH_SOURCE[0]}")/../settings/main.sh"
source "${BASHSMITH_LIB}/cli.sh"

NAMESPACE::usage() {
  printf 'Usage: %s [options]\n\n' "$(basename "$0")"
  printf 'Options:\n'
  printf '  -h, --help    Show this help\n'
}

NAMESPACE::main() {
  case "${1:-}" in
    -h|--help) NAMESPACE::usage; return 0 ;;
    *)
      # TODO: implement main logic
      Return::success "done"
      ;;
  esac
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && NAMESPACE::main "$@"
```

---

### bin/run — Full (TUI) mode

```bash
#!/usr/bin/env bash
# bin/run — PROJECT_NAME interactive entry point.
# Sources settings first, then uses Gum adapter for all TUI interactions.

source "$(dirname "${BASH_SOURCE[0]}")/../settings/main.sh"

if command -v gum &>/dev/null; then
  # shellcheck source=/dev/null
  source "${BASHSMITH_LIB}/gum.sh"
  HAVE_GUM=1
else
  HAVE_GUM=0
fi

# ── Menu items ─────────────────────────────────────────────────────────────────
# Format: "label:description"
MENU_ITEMS=(
  "run:Run the main task"
  "quit:Exit"
)

# ── Menu display ────────────────────────────────────────────────────────────────
NAMESPACE::menu() {
  if [[ "$HAVE_GUM" == "1" ]]; then
    printf '%s\n' "${MENU_ITEMS[@]}" \
      | gum choose \
          --header "PROJECT_NAME — What would you like to do?" \
          --cursor "> " \
          --cursor.foreground "${BASHSMITH_GUM_COLOR_PRIMARY:-212}" \
          --selected.foreground 82
  else
    local i=1
    printf '\nPROJECT_NAME — What would you like to do?\n\n'
    for item in "${MENU_ITEMS[@]}"; do
      printf '  %d. %s\n' "$i" "${item%%:*}"
      i=$((i + 1))
    done
    printf '\n'
    read -r -p "Enter selection: " num
    local idx=$((num - 1))
    echo "${MENU_ITEMS[$idx]:-quit}"
  fi
}

# ── Main ───────────────────────────────────────────────────────────────────────
NAMESPACE::main() {
  local choice
  Gum::catch_ctrlc 2>/dev/null || true

  choice=$(NAMESPACE::menu) || {
    [[ "$HAVE_GUM" == "1" ]] && gum style --foreground 196 "Interrupted."
    return 130
  }

  [[ -z "$choice" ]] && return 1

  local action="${choice%%:*}"
  case "$action" in
    run)  NAMESPACE::run ;;
    quit) return 0 ;;
    *)
      [[ "$HAVE_GUM" == "1" ]] && gum style --foreground 196 "Unknown: ${action}"
      return 1
      ;;
  esac
}

# ── Commands ───────────────────────────────────────────────────────────────────
NAMESPACE::run() {
  # TODO: implement main logic
  Return::success "done"
}

# ── Bootstrap ─────────────────────────────────────────────────────────────────
[[ "${BASH_SOURCE[0]}" == "${0}" ]] && NAMESPACE::main "$@"
```

---

### bats/<project-name>_test.bats

Use the kebab-case project name as the filename, e.g. `bats/my-tool_test.bats`.

```bash
#!/usr/bin/env bats
# bats/PROJECT_NAME_test.bats — Test suite for PROJECT_NAME.

setup() {
  BATS_TEST_DIRNAME="$(cd "$(dirname "$BATS_TEST_FILENAME")" && pwd)"
  PROJECT_ROOT="$(cd "${BATS_TEST_DIRNAME}/.." && pwd)"
  export PROJECT_ROOT
}

@test "bin/run exists and is executable" {
  [ -x "${PROJECT_ROOT}/bin/run" ]
}

@test "settings/main.sh loads without error" {
  run bash -c "source ${PROJECT_ROOT}/settings/main.sh && echo ok"
  [ "$status" -eq 0 ]
  [ "$output" = "ok" ]
}

@test "Return::success emits ok status" {
  run bash -c "source ${PROJECT_ROOT}/settings/main.sh && Return::success 'hello'"
  [ "$status" -eq 0 ]
  [[ "$output" == *'"status":"ok"'* ]]
}
```

---

### README.md — Minimal mode

```markdown
# PROJECT_NAME

> Brief description.

## Requirements

- bash 4.0+
- [jq](https://stedolan.github.io/jq/) — JSON processing
- [shellcheck](https://www.shellcheck.net/) — linting (dev)
- [bats](https://bats-core.readthedocs.io/) — testing (dev)

## Usage

\`\`\`bash
./bin/setup            # Initial project setup & dependencies
./bin/run              # Run entry point
./bin/qa               # Run quality checks (shellcheck + bats)
BASHSMITH_DEBUG=1 ./bin/run  # Enable debug trace
\`\`\`

## Project structure

\`\`\`
PROJECT_NAME/
├── bin/
│   ├── setup        # Environment/dependency setup
│   ├── run          # Entry point
│   └── qa           # Quality gate (shellcheck + bats)
├── lib/
│   ├── bootstrap.sh # Robust system/dep detection logic
│   ├── monad.sh     # JSON return monad
│   └── cli.sh       # CLI option processor
├── settings/
│   └── main.sh      # Strict mode + env config
├── bats/            # BATS tests
└── .shellcheckrc    # Lint config
\`\`\`
```

---

### README.md — Full (TUI) mode

Same as Minimal but add to **Requirements**:
```
- [gum](https://github.com/charmbracelet/gum) — TUI (`brew install charmbracelet/tap/gum`)
```

And add to the **Project structure** tree under `lib/`:
```
│   └── gum.sh       # TUI adapter (Gum::* wrappers)
```
