# TUI Patterns (Gum)

Standardized patterns for building terminal UIs in bashsmithing projects using
**gum** (Charm's CLI tools). All gum calls should go through the `Gum::*` adapter
in `lib/gum.sh` — never call `gum` directly. This isolates gum's CLI surface so
API or flag changes only need updating in one place.

> **Verify gum flags** before generating code: activate `bashsmithing-context`
> and check `/charmbracelet/gum` for the latest syntax.

---

## gum Adapter (`lib/gum.sh`)

The adapter wraps the gum CLI with theme defaults and Bash-friendly error handling.

| Adapter function | Wraps gum | Purpose |
|---|---|---|
| `Gum::choose_single` | `gum choose` | Single selection menu |
| `Gum::choose_multi` | `gum choose --no-limit` | Multi-selection |
| `Gum::choose_from_file` | `gum choose < file` | Single from file |
| `Gum::menu_main` | `gum choose` | Titled menu with descriptions |
| `Gum::input` | `gum input` | Single-line text input |
| `Gum::input_required` | `gum input` + loop | Non-empty validation |
| `Gum::write` | `gum write` | Multi-line input (Ctrl+D) |
| `Gum::spin` | `gum spin` | Spinner during long task |
| `Gum::confirm` | `gum confirm` | Yes/no prompt |
| `Gum::confirm_destructive` | `gum confirm` | Styled destructive guard |
| `Gum::filter_single` | `gum filter` | Fuzzy single select |
| `Gum::filter_multi` | `gum filter` | Fuzzy multi select |
| `Gum::table_csv` | `gum table` | Render CSV table |
| `Gum::box` | `gum style` | Styled text box |
| `Gum::header` | `gum style` | Section header |
| `Gum::pager` | `gum pager` | Scrollable content |

---

## 1. Main Menu Loop

The application entry point. Uses `gum choose` for the main menu with
fallback to a read-based menu if gum is not installed.

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

source settings/main.sh
source "${BASHSMITH_LIB}/gum.sh"
source "${BASHSMITH_LIB}/monad.sh"

# Menu items: "label:description"
MENU_ITEMS=(
  "scan:Scan for open ports"
  "deploy:Deploy to environment"
  "logs:Tail application logs"
  "config:Edit configuration"
  "quit:Exit"
)

# Trap Ctrl+C cleanly.
Gum::catch_ctrlc

# Build the menu from items.
build_menu() {
  local title="${1:?Title required}"; shift
  printf '%s\n' "$@" | gum choose --header "$title"
}

main() {
  while true; do
    clear
    Gum::header "NetScan CLI"

    local choice
    choice=$(printf '%s\n' "${MENU_ITEMS[@]}" | gum choose --cursor "> " \
      --header "Select an action:" \
      --selected.foreground 82)

    local action="${choice%%:*}"

    case "$action" in
      scan)    run_scan ;;
      deploy)  run_deploy ;;
      logs)    run_logs ;;
      config)  edit_config ;;
      quit)    Gum::success "Goodbye!"; break ;;
      *)       Gum::error "Unknown action: $action" ;;
    esac

    # Pause so user can read output before the next menu.
    gum input --placeholder "Press Enter to continue..." > /dev/null
  done
}

main "$@"
```

---

## 2. gum choose — Interactive Menus

### Single selection (most common)

```bash
local choice
choice=$(gum choose "Deploy" "Rollback" "Cancel")
if [[ -z "$choice" ]]; then
  Gum::error "No selection made."
  return 1
fi
```

### Single selection from an array

```bash
local -a OPTIONS=("Production" "Staging" "Development")
local env
env=$(printf '%s\n' "${OPTIONS[@]}" | gum choose --header "Select environment:")
```

### Multi-selection with limit

```bash
# Select up to 5 servers
local servers
servers=$(gum choose --limit 5 \
  "server-01" "server-02" "server-03" "server-04" "server-05" \
  "server-06" "server-07" "server-08")
```

### Multi-selection with all allowed

```bash
local plugins
plugins=$(cat plugins.txt | gum choose --no-limit --header "Select plugins to install:")
echo "$plugins" | while IFS= read -r plugin; do
  echo "Installing: $plugin"
done
```

### Pre-selected options

```bash
local langs
langs=$(gum choose \
  --selected "Ruby" \
  --selected "Bash" \
  "Ruby" "Bash" "Python" "Go" "Rust")
```

### Custom cursor and highlight colors

```bash
local choice
choice=$(gum choose \
  --cursor "> " \
  --cursor.foreground 212 \
  --selected.foreground 82 \
  "Option A" "Option B" "Option C")
```

---

## 3. gum input — Text Entry

### Basic text input

```bash
local name
name=$(gum input --placeholder "Enter your name")
echo "Hello, $name"
```

### Input with pre-filled default

```bash
local host
host=$(gum input \
  --placeholder "Hostname" \
  --value "localhost" \
  --prompt "Host: ")
```

### Password input (masked)

```bash
local password
password=$(gum input \
  --password \
  --placeholder "API key" \
  --prompt "Key: ")
```

### Required input with validation loop

```bash
local email
while true; do
  email=$(gum input --placeholder "user@example.com" --prompt "Email: ")
  if [[ "$email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
    break
  fi
  Gum::error "Invalid email. Try again."
done
echo "Got: $email"
```

### Multiple inputs in sequence

```bash
local name email role
name=$(gum input --placeholder "Full name")
email=$(gum input --placeholder "Email address")
role=$(printf '%s\n' "Admin" "User" "Guest" | gum choose --header "Role:")

cat <<EOF
Name:  $name
Email: $email
Role:  $role
EOF
```

---

## 4. gum write — Multi-line Input

### Basic multi-line (Ctrl+D to finish)

```bash
local description
description=$(gum write --placeholder "Enter a description...")

# Save to file
echo "$description" > description.txt
```

### Multi-line with character limit

```bash
local changelog
changelog=$(gum write \
  --placeholder "Changelog entry..." \
  --char-limit 280)
```

### Pre-filled multi-line input

```bash
local commit_msg
commit_msg=$(gum write \
  --value "Fix: correct edge case in user auth

BREAKING CHANGE: drops support for legacy token format
" \
  --placeholder "Edit commit message...")
```

---

## 5. gum spin — Long-running Tasks

### Basic spinner

```bash
Gum::spin "Scanning ports..." nmap -sS localhost
```

### With spinner style

```bash
local result
result=$(Gum::spin_custom \
  "Cloning repository..." \
  globe \
  git clone "$repo_url" /tmp/repo)
```

### Spin with visible command output

```bash
gum spin \
  --title "Installing packages..." \
  --show-output \
  --spinner dot \
  npm install
```

### Multiple parallel spinners (background jobs + gum spin for each)

```bash
# Spin while a command runs; combine with Return monads
result=$(Gum::spin "Fetching config..." \
  bash -c 'curl -s https://api.example.com/config')
if Return::is_ok "$result"; then
  config=$(Return::data "$result")
fi
```

---

## 6. gum confirm — Action Guards

### Basic confirmation

```bash
if gum confirm "Deploy to production?"; then
  Gum::spin "Deploying..." deploy.sh --env production
  Gum::success "Deployed successfully."
else
  Gum::info "Deployment cancelled."
fi
```

### Guard for destructive action

```bash
Gum::confirm_destructive() {
  local action="${1:?Action required}"
  gum confirm \
    --affirmative "Delete" \
    --negative "Cancel" \
    "$(gum style --foreground 196 "⚠  Delete: $action")"
}

if Gum::confirm_destructive "ALL DATA in /var/data"; then
  rm -rf /var/data
fi
```

### Chained: confirm then proceed

```bash
gum confirm "Commit changes?" && \
  git commit -m "$SUMMARY" -m "$DESCRIPTION"
```

---

## 7. gum filter — Fuzzy Search

### Filter from array

```bash
local file
file=$(printf '%s\n' "${all_files[@]}" | \
  gum filter --limit 1 --placeholder "Search files...")
echo "Editing: $file"
```

### Filter git branches

```bash
local branch
branch=$(git branch | choose -c 2: | \
  gum filter --limit 1 --placeholder "Switch to branch...")
git checkout "$branch"
```

### Multi-select with unlimited

```bash
local selected
selected=$(cat <<'EOF' | gum filter --no-limit --header "Select packages:"
bashsmith
rubysmithing
bashsmithing-context
bashsmithing-tui
bashsmithing-refactor
bashsmithing-report
EOF
)
echo "Selected: $selected"
```

### Filter with custom styling

```bash
local choice
choice=$(cat packages.txt | gum filter \
  --indicator "→ " \
  --match.foreground 212 \
  --placeholder "Search packages...")
```

---

## 8. gum table — Structured Data

### Basic table from CSV

```bash
# data.csv: Name,IP,Status
# Strawberry,10.0.0.1,Active
# Banana,10.0.0.2,Active
# Cherry,10.0.0.3,Maintenance

gum table < data.csv
```

### Table with custom column widths and styling

```bash
gum table \
  --columns "Name,IP,Status" \
  --widths 20,15,12 \
  --border rounded \
  --border.foreground 57 \
  --foreground 212 \
  < data.csv
```

### Print all rows without selection (no cursor)

```bash
gum table --print < data.csv
```

### Table from JSON (via jq)

```bash
# Extract fields and format as CSV for gum table
cat data.json | jq -r '.[] | [.name, .ip, .status] | @csv' | \
  gum table --columns "Name,IP,Status"
```

---

## 9. gum style — Text Styling

### Colored text

```bash
gum style --foreground 196 "Error: something went wrong"
gum style --foreground 82 "Success: deployed"
gum style --foreground 240 --italic "This is muted and italic"
```

### Bordered box

```bash
BOX=$(gum style \
  --border rounded \
  --border-foreground 212 \
  --padding "1 2" \
  --width 40 \
  "Ready to deploy")
echo "$BOX"
```

### Header separator

```bash
gum style --bold --foreground 212 "══ Deploy Menu ══"
```

### Multi-line styled block

```bash
gum style \
  --foreground 212 --border double --border-foreground 212 \
  --align center --width 50 --margin "1 2" --padding "2 4" \
  "Bubble Gum (1¢)" "So sweet and so fresh!"
```

---

## 10. gum pager — Scrollable Content

### Basic paging

```bash
gum pager < README.md
```

### With line numbers

```bash
gum pager --show-line-numbers < CHANGELOG.md
```

### Soft-wrap long lines

```bash
gum pager --soft-wrap < log_file.txt
```

### With search highlight

```bash
gum pager \
  --match-style "foreground:196,bold" \
  < output.log
```

---

## 11. Combining Gum with Return Monads

gum outputs data via stdout. Wrap gum calls with Return monads for
structured error handling.

### gum input → monad

```bash
Prompt::ask_name() {
  local prompt="${1:-Name:}"
  local name
  name=$(gum input --placeholder "Your name" --prompt "$prompt") || {
    Return::failure "gum input interrupted"
    return 1
  }
  [[ -z "$name" ]] && Return::failure "name cannot be empty"
  Return::success "$name"
}
```

### gum spin → monad

```bash
Task::run_scan() {
  local target="${1:?Target required}"
  local result

  # Capture spinner output
  result=$(gum spin \
    --title "Scanning ${target}..." \
    --spinner dot \
    nmap -sS -T4 "$target" 2>&1) || {
    Return::failure "scan failed: $result"
    return 1
  }

  Return::success "$result"
}
```

### gum confirm → monad

```bash
Guard::destructive() {
  local action="${1:?Action required}"
  gum confirm \
    --affirmative "Proceed" \
    --negative "Abort" \
    "$(gum style --foreground 196 "⚠  $action — are you sure?")" \
    && Return::success "confirmed" \
    || Return::failure "aborted by user"
}
```

---

## 12. Exit Handling — Ctrl+C and Empty Input

### Trap Ctrl+C during gum interaction

```bash
trap 'echo ""; gum style --foreground 196 "Interrupted."; exit 130' INT

choice=$(gum choose "A" "B" "C")
# If user presses Ctrl+C here, the trap fires cleanly.
```

### Check for empty selection (user pressed Esc or Enter with no choice)

```bash
choice=$(gum choose "A" "B" "C" 2>/dev/null)
if [[ -z "$choice" ]]; then
  Gum::info "No selection — returning to menu."
  return 0
fi
```

### Read fallback when gum is unavailable

```bash
get_choice() {
  if command -v gum &>/dev/null; then
    gum choose "$@"
  else
    # Plain read fallback
    local -a options=("$@")
    local i=1
    for opt in "$@"; do
      echo "  $i. $opt"
      i=$((i + 1))
    done
    read -r num
    echo "${options[$((num - 1))]:-}"
  fi
}
```

---

## 13. Theme Configuration

Set theme globally via env vars in `settings/main.sh`:

```bash
# Theme: simple, catppuccin, Dracula, fourk (default: simple)
export BASHSMITH_GUM_THEME="${BASHSMITH_GUM_THEME:-simple}"

# Color overrides (ANSI 256 color codes)
export BASHSMITH_GUM_COLOR_PRIMARY="${BASHSMITH_GUM_COLOR_PRIMARY:-212}"
export BASHSMITH_GUM_COLOR_SECONDARY="${BASHSMITH_GUM_COLOR_SECONDARY:-57}"
export BASHSMITH_GUM_COLOR_ERROR="${BASHSMITH_GUM_COLOR_ERROR:-196}"
export BASHSMITH_GUM_COLOR_SUCCESS="${BASHSMITH_GUM_COLOR_SUCCESS:-82}"
```

Or override per-call with gum's own flags:

```bash
gum choose \
  --cursor.foreground 99 \
  --selected.foreground 82 \
  --header.foreground 240 \
  "A" "B" "C"
```

---

## 14. Complete Scaffold Skeleton

For new TUI projects, produce this directory layout:

```
myproject/
├── bin/
│   └── run              # Entry point — sources lib + Gum::main
├── lib/
│   ├── gum.sh           # Gum adapter (always source this)
│   ├── monad.sh         # Return::success / Return::failure
│   └── menu.sh          # Menu definitions
├── settings/
│   └── main.sh          # BASHSMITH_GUM_THEME + paths
└── bats/
    └── run_test.bats   # BATS tests for each Gum::* function
```

The `bin/run` entry point template:

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

BASHSMITH_ROOT="${BASHSMITH_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"
export BASHSMITH_ROOT
export BASHSMITH_LIB="${BASHSMITH_LIB:-${BASHSMITH_ROOT}/lib}"
export BASHSMITH_SETTINGS="${BASHSMITH_SETTINGS:-${BASHSMITH_ROOT}/settings}"

source "${BASHSMITH_SETTINGS}/main.sh"
source "${BASHSMITH_LIB}/monad.sh"
source "${BASHSMITH_LIB}/gum.sh"

main() {
  local choice
  Gum::catch_ctrlc

  MENU_ITEMS=(
    "item1:Do thing one"
    "item2:Do thing two"
    "quit:Exit"
  )

  choice=$(printf '%s\n' "${MENU_ITEMS[@]}" | gum choose --header "My App")
  local action="${choice%%:*}"

  case "$action" in
    item1) Gum::spin "Working..." my_command ;;
    item2) my_other_command ;;
    quit)  return 0 ;;
    *)     Gum::error "Unknown: $action" ;;
  esac
}

main "$@"
```

---

## 15. Few-Shot Pattern Examples

Complete, runnable examples for each layout paradigm. All gum flags verified
against current CLI syntax via Context7 `/charmbracelet/gum`.

---

### Pattern A — Persistent Multi-Panel (`gum join`)

Two-panel layout: navigation list on the left, detail view on the right.
Each panel is a styled string block; `gum join` composes them horizontally.

**Critical:** always quote variables passed to `gum join` — unquoted args lose
newlines and break border rendering.

```bash
#!/usr/bin/env bash
# bin/run — Persistent multi-panel example
set -euo pipefail
IFS=$'\n\t'

source "$(dirname "${BASH_SOURCE[0]}")/../settings/main.sh"
source "${BASHSMITH_LIB}/gum.sh"

# ── Data ──────────────────────────────────────────────────────────────────────
declare -A ITEMS=(
  [api-server]="Port: 8080\nStatus: running\nUptime: 3d 2h"
  [worker]="Port: N/A\nStatus: running\nUptime: 3d 2h"
  [scheduler]="Port: N/A\nStatus: stopped\nUptime: 0"
)
ITEM_NAMES=("api-server" "worker" "scheduler")

# ── Panels ────────────────────────────────────────────────────────────────────
Panel::nav() {
  local selected="${1:-}"
  local lines=""
  for name in "${ITEM_NAMES[@]}"; do
    if [[ "$name" == "$selected" ]]; then
      lines+="$(gum style --foreground "${GUM_COLOR_PRIMARY}" "> ${name}")\n"
    else
      lines+="  ${name}\n"
    fi
  done
  # --width forces fixed panel size so gum join aligns correctly
  gum style \
    --border rounded \
    --border-foreground "${GUM_COLOR_MUTED}" \
    --padding "1 2" \
    --width 22 \
    "$(printf '%b' "$lines")"
}

Panel::detail() {
  local item="${1:-}"
  local content="${ITEMS[$item]:-Select an item}"
  gum style \
    --border rounded \
    --border-foreground "${GUM_COLOR_PRIMARY}" \
    --padding "1 3" \
    --width 44 \
    "$(gum style --bold "$item")" \
    "" \
    "$(printf '%b' "$content")"
}

Panel::footer() {
  gum style --foreground "${GUM_COLOR_MUTED}" \
    "[↑↓]navigate  [Enter]select  [q]quit  [?]help"
}

# ── Layout ────────────────────────────────────────────────────────────────────
Layout::render() {
  local selected="${1:-}"
  local nav detail
  nav=$(Panel::nav "$selected")
  detail=$(Panel::detail "$selected")
  # Quote both args — required to preserve newlines inside border sequences
  gum join --horizontal --align top "$nav" "$detail"
}

# ── Main ──────────────────────────────────────────────────────────────────────
MultiPanel::main() {
  trap 'printf "\n"; exit 130' INT
  local selected="${ITEM_NAMES[0]}"

  while true; do
    clear
    Layout::render "$selected"
    Panel::footer

    local choice
    choice=$(printf '%s\n' "${ITEM_NAMES[@]}" \
      | gum choose \
          --header "Select service:" \
          --cursor "> " \
          --cursor.foreground "${GUM_COLOR_PRIMARY}" \
          --selected.foreground "${GUM_COLOR_PRIMARY}") || break

    [[ "$choice" == "q" || -z "$choice" ]] && break
    selected="$choice"
  done
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && MultiPanel::main "$@"
```

---

### Pattern B — Drill-Down Stack with Breadcrumb

Screen stack navigation: `Enter` descends, `Esc` ascends. Breadcrumb renders
at the top of every screen using `Nav::breadcrumb`.

```bash
#!/usr/bin/env bash
# bin/run — Drill-down stack example
set -euo pipefail
IFS=$'\n\t'

source "$(dirname "${BASH_SOURCE[0]}")/../settings/main.sh"
source "${BASHSMITH_LIB}/gum.sh"
source "${BASHSMITH_LIB}/nav.sh"

# ── lib/nav.sh ────────────────────────────────────────────────────────────────
# (contents shown inline for this example; extract to lib/nav.sh in real scaffold)
declare -a _NAV_STACK=()

Nav::push()  { _NAV_STACK+=("$1"); }
Nav::pop()   { [[ ${#_NAV_STACK[@]} -gt 0 ]] && unset '_NAV_STACK[-1]'; }
Nav::current() { echo "${_NAV_STACK[-1]:-home}"; }
Nav::breadcrumb() {
  local IFS=" > "
  gum style --foreground "${GUM_COLOR_MUTED}" "${_NAV_STACK[*]:-home}"
}
Nav::depth()   { echo "${#_NAV_STACK[@]}"; }

# ── Screen renderers ──────────────────────────────────────────────────────────
Screen::home() {
  local -a environments=("production" "staging" "development" "← back")
  clear
  Nav::breadcrumb
  gum style --bold --foreground "${GUM_COLOR_PRIMARY}" "Environments"

  local choice
  choice=$(printf '%s\n' "${environments[@]}" \
    | gum choose \
        --header "Select environment:" \
        --cursor.foreground "${GUM_COLOR_PRIMARY}" \
        --selected.foreground "${GUM_COLOR_PRIMARY}") || return 0

  case "$choice" in
    "← back") return 0 ;;
    *)
      Nav::push "$choice"
      Screen::environment "$choice"
      Nav::pop
      ;;
  esac
}

Screen::environment() {
  local env="${1:?}"
  local -a services=("api-server" "worker" "scheduler" "← back")
  clear
  Nav::breadcrumb
  gum style --bold --foreground "${GUM_COLOR_PRIMARY}" "Services in ${env}"

  local choice
  choice=$(printf '%s\n' "${services[@]}" \
    | gum choose \
        --header "Select service:" \
        --cursor.foreground "${GUM_COLOR_PRIMARY}") || return 0

  case "$choice" in
    "← back") return 0 ;;
    *)
      Nav::push "$choice"
      Screen::service "$env" "$choice"
      Nav::pop
      ;;
  esac
}

Screen::service() {
  local env="${1:?}" service="${2:?}"
  clear
  Nav::breadcrumb
  gum style --bold --foreground "${GUM_COLOR_PRIMARY}" "${service}"
  printf '\n'
  printf 'Environment: %s\nStatus:      running\nReplicas:    3\n' "$env"
  printf '\n'
  gum style --foreground "${GUM_COLOR_MUTED}" "[r]restart  [s]scale  [Esc/Enter]back"

  local action
  action=$(gum choose "restart" "scale" "back" \
    --header "Action:" \
    --cursor.foreground "${GUM_COLOR_PRIMARY}") || return 0

  case "$action" in
    restart)
      if gum confirm "Restart ${service} in ${env}?" \
           --affirmative="Yes, restart" \
           --negative="Cancel" \
           --selected.foreground="${GUM_COLOR_PRIMARY}"; then
        gum spin --title "Restarting ${service}..." -- sleep 2
        gum style --foreground "${GUM_COLOR_SUCCESS}" "✓ Restarted"
      fi
      ;;
    scale)
      local replicas
      replicas=$(gum input --placeholder "Number of replicas" --prompt "Replicas: ")
      gum spin --title "Scaling to ${replicas}..." -- sleep 2
      gum style --foreground "${GUM_COLOR_SUCCESS}" "✓ Scaled to ${replicas}"
      ;;
  esac

  gum input --placeholder "Press Enter to continue..." > /dev/null
}

# ── Main ──────────────────────────────────────────────────────────────────────
DrillDown::main() {
  trap 'printf "\n"; exit 130' INT
  Nav::push "home"
  while true; do
    Screen::home
    # If stack is back to just "home", the user backed all the way out
    [[ $(Nav::depth) -le 1 ]] && break
  done
  printf '\n'
  gum style --foreground "${GUM_COLOR_MUTED}" "Goodbye."
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && DrillDown::main "$@"
```

---

### Pattern C — HITL Orchestration (Human-in-the-Loop)

Five-step pattern: Generate → Display for review → Verify → Execute → Log.
Uses `gum filter` for selective approval, `gum confirm` for final gate,
`gum spin` for execution, and `gum pager` to review output.

```bash
#!/usr/bin/env bash
# lib/hitl.sh — Human-in-the-Loop orchestration pattern
set -euo pipefail
IFS=$'\n\t'

# ── Step 1: Generate ──────────────────────────────────────────────────────────
# Build the proposed action list. Returns newline-separated strings to stdout.
Hitl::generate_actions() {
  local target_dir="${1:?Target dir required}"
  # Example: find log files older than 7 days
  fd -t f -e log --changed-before 7d "$target_dir" 2>/dev/null
}

# ── Step 2: Display & Step 3: Verify ─────────────────────────────────────────
# Shows proposed actions via gum filter (user toggles what to include),
# then gates execution through gum confirm.
Hitl::review_and_confirm() {
  local -a actions=("$@")

  if [[ ${#actions[@]} -eq 0 ]]; then
    gum style --foreground "${GUM_COLOR_MUTED}" "• No actions proposed."
    Return::success "none"
    return 0
  fi

  # Display — user selects which actions to include
  # fzf alternative (supports preview): printf '%s\n' "${actions[@]}" | fzf --multi \
  #   --height 40% --preview 'echo {}' --preview-window down:3:wrap \
  #   --header "Review proposed actions (Tab to toggle):" \
  #   --bind 'ctrl-a:select-all,ctrl-d:deselect-all'
  local selected
  selected=$(printf '%s\n' "${actions[@]}" \
    | gum filter \
        --no-limit \
        --header "Review proposed actions (Space to toggle, Enter to confirm):" \
        --indicator "▶" \
        --match.foreground "${GUM_COLOR_PRIMARY}") || {
    Return::failure "review cancelled"
    return 1
  }

  [[ -z "$selected" ]] && {
    gum style --foreground "${GUM_COLOR_MUTED}" "• No actions selected."
    Return::success "none"
    return 0
  }

  local count
  count=$(wc -l <<< "$selected")

  # Verify — final gate before execution
  gum confirm \
    "Execute ${count} action(s)?" \
    --affirmative="Yes, proceed" \
    --negative="Abort" \
    --selected.foreground="${GUM_COLOR_PRIMARY}" \
    --unselected.foreground="${GUM_COLOR_MUTED}" || {
    gum style --foreground "${GUM_COLOR_MUTED}" "Aborted."
    Return::failure "aborted by user"
    return 1
  }

  Return::success "$selected"
}

# ── Step 4: Execute ───────────────────────────────────────────────────────────
Hitl::execute() {
  local selected_actions="${1:?}"
  local log_file
  log_file=$(mktemp /tmp/hitl-output.XXXXXX)

  # Run each selected action inside a spinner; capture output to log
  while IFS= read -r action; do
    gum spin \
      --title "Processing: $(basename "$action")..." \
      --spinner dot \
      -- bash -c "rm -v \"$action\"" >> "$log_file" 2>&1 || {
      printf 'FAILED: %s\n' "$action" >> "$log_file"
    }
  done <<< "$selected_actions"

  Return::success "$log_file"
}

# ── Step 5: Log ───────────────────────────────────────────────────────────────
Hitl::show_log() {
  local log_file="${1:?}"
  local line_count
  line_count=$(wc -l < "$log_file")

  gum style --foreground "${GUM_COLOR_SUCCESS}" "✓ Complete — ${line_count} operation(s)"

  if [[ "$line_count" -gt 0 ]]; then
    gum pager \
      --show-line-numbers \
      < "$log_file"
  fi

  rm -f "$log_file"
}

# ── Orchestrator ──────────────────────────────────────────────────────────────
Hitl::run() {
  local target_dir="${1:?}"

  # 1. Generate
  local -a actions
  mapfile -t actions < <(Hitl::generate_actions "$target_dir")

  # 2 & 3. Display + Verify
  local review_result
  review_result=$(Hitl::review_and_confirm "${actions[@]}") || return 1
  local selected_actions
  selected_actions=$(Return::data "$review_result")

  [[ "$selected_actions" == "none" ]] && return 0

  # 4. Execute
  local exec_result
  exec_result=$(Hitl::execute "$selected_actions") || {
    gum style --foreground "${GUM_COLOR_ERROR}" "✗ Execution failed"
    return 1
  }

  # 5. Log
  Hitl::show_log "$(Return::data "$exec_result")"
}
```

---

### Pattern D — Header + Scrollable List with Live Refresh

Fixed metadata header rendered with `gum style`; live list below via
`gum filter`. Refresh loop re-queries data each cycle.

```bash
#!/usr/bin/env bash
# bin/run — Header + scrollable list example (process viewer)
set -euo pipefail
IFS=$'\n\t'

source "$(dirname "${BASH_SOURCE[0]}")/../settings/main.sh"
source "${BASHSMITH_LIB}/gum.sh"

# ── Header ────────────────────────────────────────────────────────────────────
Display::header() {
  local cpu mem disk
  cpu=$(top -bn1 2>/dev/null | grep -i 'cpu' | choose 1 || echo "N/A")
  mem=$(printf '%s/%s' \
    "$(free -h 2>/dev/null | grep 'Mem:' | choose 2)" \
    "$(free -h 2>/dev/null | grep 'Mem:' | choose 1)" 2>/dev/null || echo "N/A")
  disk=$(df -h / 2>/dev/null | tail -n +2 | choose 4 || echo "N/A")

  local stats
  stats=$(gum join --horizontal \
    "$(gum style --foreground "${GUM_COLOR_PRIMARY}" --bold "CPU: ${cpu}%")" \
    "$(gum style --foreground "${GUM_COLOR_MUTED}" "  │  ")" \
    "$(gum style --foreground "${GUM_COLOR_PRIMARY}" --bold "MEM: ${mem}")" \
    "$(gum style --foreground "${GUM_COLOR_MUTED}" "  │  ")" \
    "$(gum style --foreground "${GUM_COLOR_PRIMARY}" --bold "DISK: ${disk}")")

  gum style \
    --border rounded \
    --border-foreground "${GUM_COLOR_PRIMARY}" \
    --padding "0 2" \
    --width 60 \
    "$stats"
}

Display::footer() {
  gum style --foreground "${GUM_COLOR_MUTED}" \
    "[q]quit  [/]filter  [k]kill  [r]refresh  [?]help"
}

# ── Process list ──────────────────────────────────────────────────────────────
Display::process_list() {
  # Generate CSV for gum table; user selects a row
  local csv
  # ps -eo selects and orders fields directly; sd converts whitespace runs to CSV
  csv=$(printf 'PID,USER,CPU%%,CMD\n'
        ps --sort=-%cpu -eo pid=,user=,pcpu=,comm= 2>/dev/null \
          | head -20 \
          | sd '^\s+' '' \
          | sd '\s+' ',')

  echo "$csv" | gum table \
    --columns "PID,USER,CPU%,CMD" \
    --widths "8,12,8,32" \
    --border rounded \
    --border.foreground "${GUM_COLOR_MUTED}"
}

# ── Main ──────────────────────────────────────────────────────────────────────
HeaderList::main() {
  trap 'printf "\n"; exit 130' INT

  while true; do
    clear
    Display::header
    printf '\n'

    local selected
    selected=$(Display::process_list) || break

    [[ -z "$selected" ]] && break

    local pid
    pid=$(echo "$selected" | choose -f ',' 0)

    local action
    action=$(gum choose "kill" "details" "back" \
      --header "PID ${pid} — action:" \
      --cursor.foreground "${GUM_COLOR_PRIMARY}") || continue

    case "$action" in
      kill)
        gum confirm \
          "Kill PID ${pid}?" \
          --affirmative="Yes, kill" \
          --negative="Cancel" \
          --selected.foreground="${GUM_COLOR_ERROR}" && {
          kill "$pid" 2>/dev/null \
            && gum style --foreground "${GUM_COLOR_SUCCESS}" "✓ Killed ${pid}" \
            || gum style --foreground "${GUM_COLOR_ERROR}" "✗ Failed to kill ${pid}"
          sleep 1
        }
        ;;
      details)
        ps -p "$pid" -o pid,user,%cpu,%mem,etime,cmd 2>/dev/null \
          | gum pager --show-line-numbers
        ;;
      back) continue ;;
    esac

    Display::footer
  done
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && HeaderList::main "$@"
```

---

### Pattern E — Multi-Step Wizard (Sequential Inputs)

Collects structured data across sequential screens before executing.
Each step validates before advancing. Final confirmation shows a summary.

```bash
#!/usr/bin/env bash
# lib/wizard.sh — Multi-step form / wizard pattern
set -euo pipefail
IFS=$'\n\t'

# ── Step renderers ────────────────────────────────────────────────────────────
Wizard::step_header() {
  local step="${1:?}" total="${2:?}" title="${3:?}"
  gum style \
    --foreground "${GUM_COLOR_PRIMARY}" \
    --bold \
    "Step ${step}/${total}: ${title}"
  gum style --foreground "${GUM_COLOR_MUTED}" "$(printf '─%.0s' {1..40})"
}

Wizard::step1_project_name() {
  Wizard::step_header 1 3 "Project Name"
  local name
  while true; do
    name=$(gum input \
      --placeholder "my-tool" \
      --prompt "Name: " \
      --char-limit 50) || return 1
    # Validate: kebab-case only
    if [[ "$name" =~ ^[a-z][a-z0-9-]+$ ]]; then
      Return::success "$name"
      return 0
    fi
    gum style --foreground "${GUM_COLOR_ERROR}" "✗ Use lowercase letters, numbers, and hyphens only."
  done
}

Wizard::step2_mode() {
  Wizard::step_header 2 3 "Project Mode"
  local mode
  mode=$(gum choose \
    "minimal" \
    "full" \
    --header "Select mode (minimal = no gum dependency, full = gum TUI):" \
    --cursor.foreground "${GUM_COLOR_PRIMARY}" \
    --selected.foreground "${GUM_COLOR_PRIMARY}") || return 1
  Return::success "$mode"
}

Wizard::step3_description() {
  Wizard::step_header 3 3 "Description"
  local desc
  desc=$(gum write \
    --placeholder "Brief description of the project..." \
    --char-limit 280 \
    --width 60) || return 1
  Return::success "$desc"
}

Wizard::summary() {
  local name="${1:?}" mode="${2:?}" desc="${3:?}"
  printf '\n'
  gum style \
    --border rounded \
    --border-foreground "${GUM_COLOR_PRIMARY}" \
    --padding "1 3" \
    --width 50 \
    "$(gum style --bold "Project Summary")" \
    "" \
    "$(gum style --foreground "${GUM_COLOR_MUTED}" "Name:")  ${name}" \
    "$(gum style --foreground "${GUM_COLOR_MUTED}" "Mode:")  ${mode}" \
    "$(gum style --foreground "${GUM_COLOR_MUTED}" "Desc:")  ${desc}"
  printf '\n'
}

# ── Orchestrator ──────────────────────────────────────────────────────────────
Wizard::run() {
  trap 'printf "\n"; gum style --foreground "${GUM_COLOR_MUTED}" "Cancelled."; exit 130' INT

  clear
  gum style --bold --foreground "${GUM_COLOR_PRIMARY}" "New Project Wizard"
  printf '\n'

  # Step 1
  local r1; r1=$(Wizard::step1_project_name) || return 1
  local name; name=$(Return::data "$r1")

  printf '\n'

  # Step 2
  local r2; r2=$(Wizard::step2_mode) || return 1
  local mode; mode=$(Return::data "$r2")

  printf '\n'

  # Step 3
  local r3; r3=$(Wizard::step3_description) || return 1
  local desc; desc=$(Return::data "$r3")

  # Summary + final confirm
  clear
  Wizard::summary "$name" "$mode" "$desc"

  gum confirm \
    "Create project '${name}'?" \
    --affirmative="Create" \
    --negative="Start over" \
    --selected.foreground="${GUM_COLOR_SUCCESS}" || {
    Wizard::run  # recurse to restart
    return $?
  }

  Return::success "$(printf '{"name":"%s","mode":"%s","desc":"%s"}' "$name" "$mode" "$desc")"
}
```

---

### Pattern F — Overlay/Popup (Caller-Facing Selector)

Minimal entry point that renders over the existing terminal, outputs a
selection to stdout, and exits. Designed to be called by other scripts.

```bash
#!/usr/bin/env bash
# bin/run — Overlay/popup example
# Usage: selection=$(./bin/run [input_file])
#        echo "item1\nitem2\nitem3" | ./bin/run
set -euo pipefail
IFS=$'\n\t'

source "$(dirname "${BASH_SOURCE[0]}")/../settings/main.sh"
source "${BASHSMITH_LIB}/gum.sh"

Overlay::main() {
  local input_source="${1:-/dev/stdin}"
  local height="${GUM_OVERLAY_HEIGHT:-10}"

  local result
  result=$(gum filter \
    --placeholder "Type to search..." \
    --indicator "▶" \
    --match.foreground "${GUM_COLOR_PRIMARY}" \
    --height "$height" \
    < "$input_source") || {
    # Exit 130 on Ctrl+C / Esc — caller can detect cancelled selection
    exit 130
  }

  [[ -z "$result" ]] && exit 1

  # Output selection to stdout for caller capture
  printf '%s\n' "$result"
}

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && Overlay::main "$@"
```

Caller usage:
```bash
# File picker (fd replaces find)
selected_file=$(fd -e sh | ./bin/overlay)

# Git branch switcher (choose replaces cut)
branch=$(git branch | choose -c 2: | ./bin/overlay)
git checkout "$branch"

# With height override
GUM_OVERLAY_HEIGHT=20 selected=$(cat big-list.txt | ./bin/overlay)
```

---

### Pattern G — fzf with Preview Window

Use fzf instead of gum filter when you need a **preview pane**, **multi-select with
visual feedback**, or **shell keybinding integration** (CTRL-T / CTRL-R style).
Pairs naturally with `fd` for file input and `choose` for field extraction.

```bash
#!/usr/bin/env bash
# lib/fzf_patterns.sh — fzf integration patterns
set -euo pipefail
IFS=$'\n\t'

source "$(dirname "${BASH_SOURCE[0]}")/../settings/main.sh"

# ── File picker with syntax-highlighted preview ───────────────────────────────
# Requires: fd, fzf, bat
Fzf::file_picker() {
  local root="${1:-.}"
  local file
  file=$(fd --type f . "$root" \
    | fzf \
        --preview 'bat --color=always --line-range :50 {}' \
        --preview-window 'right,50%,border-left' \
        --height '60%' \
        --layout reverse \
        --bind 'ctrl-/:toggle-preview') || return 1
  [[ -n "$file" ]] && Return::success "$file" || Return::failure "no selection"
}

# ── Multi-select review (HITL alternative to gum filter --no-limit) ───────────
# Tab toggles selection; Enter confirms; Ctrl-A selects all; Ctrl-D deselects all
Fzf::multi_review() {
  local header="${1:-Select items (Tab to toggle, Enter to confirm):}"
  fzf \
    --multi \
    --header "$header" \
    --preview 'echo {}' \
    --preview-window 'down,3,wrap' \
    --height '50%' \
    --layout reverse \
    --bind 'ctrl-a:select-all,ctrl-d:deselect-all'
  # Exits non-zero if user presses Esc — caller should handle
}

# ── Git branch switcher with commit log preview ───────────────────────────────
# choose -c 2: strips the "* " / "  " prefix git branch adds (chars 0-1)
Fzf::branch_switch() {
  local branch
  branch=$(git branch \
    | choose -c 2: \
    | fzf \
        --preview 'git log --oneline --color=always {} | head -20' \
        --preview-window 'right,50%' \
        --height '40%') || return 1
  [[ -n "$branch" ]] && git checkout "$branch"
}

# ── Shell script editor: fd + fzf + bat preview ───────────────────────────────
Fzf::edit_script() {
  local file
  file=$(fd -e sh \
    | fzf \
        --preview 'bat --color=always {}' \
        --preview-window 'right,60%,border-left' \
        --height '80%' \
        --bind 'ctrl-/:toggle-preview') || return 1
  [[ -n "$file" ]] && "${EDITOR:-vim}" "$file"
}

# ── Log file browser: fd finds logs, fzf browses with live tail preview ───────
Fzf::log_browser() {
  local log_dir="${1:-.}"
  local file
  file=$(fd -e log -e txt . "$log_dir" \
    | fzf \
        --preview 'tail -n 50 {}' \
        --preview-window 'right,60%,wrap' \
        --height '70%' \
        --layout reverse) || return 1
  [[ -n "$file" ]] && gum pager --soft-wrap < "$file"
}
```

**gum filter vs fzf — when to choose each:**

| Need | Use |
|:-----|:----|
| Themed to match gum style system | `gum filter` |
| Preview pane for file/log content | `fzf --preview` |
| Multi-select with select-all binding | `fzf --multi` |
| Shell keybinding (CTRL-T file picker) | `fzf` |
| Simple list filter, no preview needed | `gum filter` |
| Inline in a gum-based TUI loop | `gum filter` |
