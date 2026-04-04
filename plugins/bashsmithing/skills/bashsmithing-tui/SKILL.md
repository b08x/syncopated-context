---
name: bashsmithing-tui
description: Terminal UI scaffolder and advisor for Bash projects using the Charm/Gum ecosystem. Activates on any mention of: TUI, terminal UI, terminal interface, terminal app, Gum, gum prompts, interactive menu, text input, multi-line input, spinner, confirm prompt, filter list, table rendering, markdown pager, keyboard navigation, cursor movement, human in the loop component, HIL interface, RAG viewer, agent control panel, streaming output panel, text input, spinner, list selection, metrics display, or progress bar within a Bash script context. Always runs bashsmithing-context as prerequisite for gum CLI verification. Produces paradigm-specific skeletons — skeleton shape is driven by layout paradigm selection.
---

# Bashsmithing — TUI

Scaffolder and advisor for terminal UI applications using the Bash-native Charm/Gum ecosystem.
Generates paradigm-specific skeletons against verified gum CLI syntax only.

---

## Step 0: Framework Routing (Decide Before Anything Else)

Gum is procedural and stateless — each command captures input then exits. Route away when:

| Condition | Recommend Instead |
|:----------|:-----------------|
| Persistent background tasks / async polling | Textual (Python) or Bubble Tea (Go/Ruby) |
| Reactive state shared across multiple screens | Textual |
| Full-screen event loop with real-time data refresh | Textual |
| Simple interactive prompts inside existing scripts | **Gum (this skill)** |
| Multi-step wizards, confirm flows, spinners | **Gum (this skill)** |
| Shell augmentation (picker, history search) | **Gum (this skill)** |

If routing away, state explicitly:
> "This requires [framework] — bashsmithing-tui handles gum/bash only."

---

## Step 1: Prerequisites

Before generating any code:

1. **Activate bashsmithing-context** for gum CLI verification. Confirm current gum version and available flags. Generate no code until CLI syntax is confirmed or a WARNING block is injected.
2. **Extract domain** — what does this TUI control or display?
3. **Select layout paradigm** (Step 2) — this drives the skeleton shape.
4. **Identify inputs per screen** — single-line, multi-line, selections, filters.
5. **Identify long-running tasks** — where spinners are needed.
6. **Identify HITL checkpoints** — where human approval must gate execution.

**Compound prompts** (e.g., "refactor this pipeline AND build a TUI for it"):
Handle the TUI component here. State explicitly:
> "Handling the TUI component. The pipeline component should be addressed with bashsmithing-refactor."

---

## Step 2: Detect Mode

**Scaffolding** — triggered by: create, build, scaffold, generate, write a TUI for.
Output: full paradigm-specific skeleton + complete file content.

**Advisory** — triggered by: how do I, which gum command, explain, what's the best way.
Output: recommendation + minimal snippet. No full scaffold unless asked.

---

## Step 3: Select Layout Paradigm

Choose based on the application type. The paradigm determines the skeleton shape.

| Paradigm | When to Use | Signature Extra Files |
|:---------|:------------|:----------------------|
| **Main Menu Loop** (default) | Single-purpose tool, <20 actions | `lib/menu.sh` |
| **Persistent Multi-Panel** | Multi-context tools needing simultaneous views | `lib/layout.sh`, `lib/panels/` |
| **Drill-Down Stack** | Hierarchical data navigation | `lib/nav.sh`, `lib/screens/` |
| **Overlay/Popup** | Shell augmentation called by other scripts | minimal — no loop |
| **Header + Scrollable List** | Single-list tool with a fixed metadata header | `lib/display.sh` |

See `references/design-patterns.md` for paradigm descriptions and when-to-use detail.

---

## Step 4: Paradigm-Specific Skeletons

### Main Menu Loop (default)

```
<app>/
├── bin/run
├── lib/
│   ├── gum.sh
│   ├── monad.sh
│   └── menu.sh          # MENU_ITEMS array + dispatch
├── settings/
│   └── main.sh
└── bats/
    └── <app>_test.bats
```

`bin/run` entry pattern:
```bash
#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/../settings/main.sh"
source "${BASHSMITH_LIB}/gum.sh"
source "${BASHSMITH_LIB}/menu.sh"

NAMESPACE::main() {
  Gum::catch_ctrlc
  while true; do
    local choice action
    choice=$(Menu::show) || break
    action="${choice%%:*}"
    case "$action" in
      quit) break ;;
      *)    Menu::dispatch "$action" ;;
    esac
    gum input --placeholder "Press Enter to continue..." > /dev/null
  done
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && NAMESPACE::main "$@"
```

---

### Persistent Multi-Panel

```
<app>/
├── bin/run
├── lib/
│   ├── gum.sh
│   ├── monad.sh
│   ├── layout.sh          # Layout::render — gum join composition
│   └── panels/
│       ├── panel_nav.sh   # left/navigation panel
│       └── panel_main.sh  # primary content panel
├── settings/
│   └── main.sh
└── bats/
    └── <app>_test.bats
```

**Key constraint:** Each panel function returns a styled string block via `gum style`. `layout.sh` composes them with `gum join`. **Always quote variables before `gum join`** — unquoted strips newlines and breaks borders.

```bash
# lib/layout.sh
Layout::render() {
  local nav main
  nav=$(Panel::nav)
  main=$(Panel::main)
  # Quote both args — newlines inside border sequences must survive
  gum join --horizontal --align top "$nav" "$main"
}
```

Panels maintain fixed positions across the session. Never rearrange without explicit user action.

---

### Drill-Down Stack

```
<app>/
├── bin/run
├── lib/
│   ├── gum.sh
│   ├── monad.sh
│   ├── nav.sh             # Nav::push, Nav::pop, Nav::breadcrumb
│   └── screens/
│       ├── screen_home.sh
│       └── screen_detail.sh
├── settings/
│   └── main.sh
└── bats/
    └── <app>_test.bats
```

**Key pattern:** `nav.sh` maintains a screen stack in a Bash array. Always render `Nav::breadcrumb` at the top of each screen so users know where they are.

```bash
# lib/nav.sh
declare -a _NAV_STACK=()

Nav::push() {
  _NAV_STACK+=("$1")
}
Nav::pop() {
  [[ ${#_NAV_STACK[@]} -gt 0 ]] && unset '_NAV_STACK[-1]'
}
Nav::breadcrumb() {
  local IFS=' > '
  echo "${_NAV_STACK[*]}"
}
Nav::current() {
  echo "${_NAV_STACK[-1]:-home}"
}
```

Screen functions call `Nav::push` on entry and `Nav::pop` on `Esc`/back. `Enter` descends, `Esc` ascends.

---

### Overlay/Popup

```
<app>/
├── bin/run     # Outputs selection to stdout, exits immediately
├── lib/
│   ├── gum.sh
│   └── monad.sh
└── settings/
    └── main.sh
```

**Key pattern:** Designed to be called from other scripts. Outputs to stdout. No `while true` loop. Caller captures the result:

```bash
# Caller: selection=$(./bin/run)
```

`bin/run` entry pattern:
```bash
#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/../settings/main.sh"
source "${BASHSMITH_LIB}/gum.sh"

NAMESPACE::main() {
  local input_source="${1:-/dev/stdin}"
  local result
  result=$(gum filter \
    --placeholder "Select..." \
    --limit 1 \
    < "$input_source") || return 130
  [[ -z "$result" ]] && Return::failure "no selection" && return 1
  Return::success "$result"
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && NAMESPACE::main "$@"
```

---

### Header + Scrollable List

```
<app>/
├── bin/run
├── lib/
│   ├── gum.sh
│   ├── monad.sh
│   └── display.sh    # Display::header, Display::list, Display::status_bar, Display::footer
├── settings/
│   └── main.sh
└── bats/
    └── <app>_test.bats
```

**Key pattern:** `display.sh` renders a fixed header block via `gum style`, then pipes list data into `gum filter` or `gum table` below it. The header creates a natural "overview then detail" reading flow.

```bash
# lib/display.sh
Display::header() {
  local title="${1:?}" subtitle="${2:-}"
  gum style \
    --border rounded \
    --border-foreground "${GUM_COLOR_PRIMARY}" \
    --padding "0 2" --width 60 \
    "$(gum style --bold "$title")" \
    "$subtitle"
}

Display::footer() {
  gum style --foreground "${GUM_COLOR_MUTED}" \
    "[q]uit  [/]search  [?]help  [Enter]select  [Tab]focus"
}
```

---

## Step 5: Interaction Model

Apply these patterns to **every** scaffold regardless of paradigm.

### Keyboard Layers

| Layer | Keys | Always Visible? |
|:------|:-----|:----------------|
| **L0: Universal** | Arrow keys, Enter, Esc, q | Yes — footer |
| **L1: Actions** | Single mnemonics: d(elete), r(efresh), ? | On `?` help |
| **L2: Power** | Composed shortcuts, flags | Docs / `--help` |

Always generate a footer stub:
```bash
Display::footer() {
  gum style --foreground "${GUM_COLOR_MUTED}" \
    "[q]uit  [?]help  [Enter]select"
}
```

Context-sensitive: update the footer per active screen or panel.

### Help System — Three Tiers

Always generate stubs for all three:

1. **Footer** (always visible) — 3–5 essential shortcuts, rendered at bottom of every screen
2. **`?` overlay** (on demand) — full keybinding list for current context, rendered via `gum pager`
3. **`--help` flag** — handled in `bin/run` argument parsing before the main loop

### Dialog Severity

| Severity | Pattern |
|:---------|:--------|
| Reversible | Execute immediately; show status via `Gum::success` |
| Moderate (delete file) | `gum confirm "Delete $file?"` |
| Severe (drop data) | `Gum::confirm_destructive` with resource name echoed |
| Irreversible batch | `--dry-run` flag + `Gum::confirm_destructive` |

### HITL Orchestration Pattern

For any action that modifies state or invokes external commands, follow this five-step loop:

1. **Generate** — build the proposed action list (array, CSV, or JSON)
2. **Display** — show via `gum filter` (interactive) or `gum table` (read-only) for review
3. **Verify** — `Gum::confirm_destructive` gates execution; abort on denial
4. **Execute** — run inside `Gum::spin`; capture stdout as a Return monad
5. **Log** — display result via `gum pager` or `gum log`

```bash
Hitl::run() {
  local -a actions=("$@")

  # Display for review
  local selected
  selected=$(printf '%s\n' "${actions[@]}" \
    | gum filter --no-limit --header "Review — select actions to execute:")
  [[ -z "$selected" ]] && Return::failure "no actions selected" && return 1

  # Verify
  Gum::confirm_destructive "Execute $(wc -l <<< "$selected") action(s)" || {
    Gum::info "Aborted."
    return 0
  }

  # Execute
  local result
  result=$(Gum::spin "Running..." bash -c "$selected") || {
    Return::failure "execution failed"
    return 1
  }

  # Log
  echo "$result" | gum pager
  Return::success "done"
}
```

---

## Step 6: Color Design System

Define semantic color variables in `settings/main.sh`. **Never hardcode ANSI codes in widget functions.**

```bash
# Detect color tier
if [[ "${COLORTERM:-}" == "truecolor" || "${COLORTERM:-}" == "24bit" ]]; then
  BASHSMITH_COLOR_TIER=truecolor
elif [[ "${TERM:-}" == *256color* ]]; then
  BASHSMITH_COLOR_TIER=256
else
  BASHSMITH_COLOR_TIER=16
fi
export BASHSMITH_COLOR_TIER

# Semantic color slots (256-color defaults)
export GUM_COLOR_PRIMARY="${GUM_COLOR_PRIMARY:-212}"    # interactive elements, focus
export GUM_COLOR_SECONDARY="${GUM_COLOR_SECONDARY:-57}" # supporting interactions
export GUM_COLOR_SUCCESS="${GUM_COLOR_SUCCESS:-82}"     # success, additions
export GUM_COLOR_ERROR="${GUM_COLOR_ERROR:-196}"        # errors, deletions
export GUM_COLOR_WARNING="${GUM_COLOR_WARNING:-214}"    # warnings, caution
export GUM_COLOR_MUTED="${GUM_COLOR_MUTED:-240}"        # metadata, footer text

# Respect NO_COLOR
if [[ -n "${NO_COLOR:-}" ]]; then
  unset GUM_COLOR_PRIMARY GUM_COLOR_SECONDARY GUM_COLOR_SUCCESS \
        GUM_COLOR_ERROR GUM_COLOR_WARNING GUM_COLOR_MUTED
fi
```

**Never rely on color as the sole signal** — always pair with a symbol and text label:

```bash
Gum::success() { gum style --foreground "${GUM_COLOR_SUCCESS:-}" "✓ $*"; }
Gum::error()   { gum style --foreground "${GUM_COLOR_ERROR:-}"   "✗ $*"; }
Gum::warning() { gum style --foreground "${GUM_COLOR_WARNING:-}" "⚠ $*"; }
Gum::info()    { gum style --foreground "${GUM_COLOR_MUTED:-}"   "• $*"; }
```

---

## Step 7: Anti-Pattern Checklist

Validate the scaffold against these before output:

| # | Anti-Pattern | Fix |
|:--|:-------------|:----|
| 1 | Calling `gum` directly instead of via adapter | All calls go through `Gum::*` in `lib/gum.sh` |
| 2 | Hardcoded ANSI color codes in widget functions | Use semantic `$GUM_COLOR_*` variables |
| 3 | No `NO_COLOR` support | Guard all color vars with `[[ -n "${NO_COLOR:-}" ]]` |
| 4 | Unquoted variables passed to `gum join` | Always quote: `gum join "$NAV" "$CONTENT"` |
| 5 | Missing `Gum::catch_ctrlc` at entry | Required in every `main()` that uses a loop |
| 6 | No footer / undiscoverable keybindings | `Display::footer` stub in every screen |
| 7 | UI blocked during long operations | All external commands wrapped in `Gum::spin` |
| 8 | Color as sole status signal | Pair every color with symbol (✓ ✗ ⚠) + text |
| 9 | No gum-absent fallback | `read`-based fallback in choose/input functions |
| 10 | Missing bootstrap guard in lib files | `[[ "${BASH_SOURCE[0]}" == "${0}" ]]` in every lib |

---

## Patterns Reference

`references/tui-patterns.md` — component recipes:
- gum choose, input, write, spin, confirm, filter, table, pager — complete patterns
- Combining gum with Return monad
- Exit handling and Ctrl+C traps
- Theme configuration

`references/design-patterns.md` — design system reference:
- Layout paradigm decision guide and visual examples
- Interaction model deep-dive (keyboard layers, focus, search)
- Semantic color slot table and accessibility requirements
- Seven design principles
- Compatibility checklist

---

## Output Format

For scaffolds:
1. **Full file tree** — paradigm-specific shape
2. **Complete content** for each file — stubs only when external tool API is undefined
3. **Boot instruction** — `chmod +x bin/<app> && ./bin/<app>`
4. **Context7 IDs used** — or WARNING blocks if resolution failed
5. **Framework routing note** if gum is the wrong tool for the request

For advisory:
1. **Direct recommendation** with rationale
2. **Minimal snippet** for the specific pattern
3. **No full scaffold** unless explicitly asked
