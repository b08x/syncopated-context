#!/usr/bin/env bash
# lib/gum.sh — gum CLI adapter for bashsmithing projects.
# Wraps the gum CLI with project defaults, theme support, and error handling.
# All gum calls should go through these functions so theme/API changes
# only need to be updated in ONE place.
#
# Usage:
#   source lib/gum.sh
#   Gum::choose_single "Option A" "Option B" "Option C"
#   Gum::input --placeholder "Enter name"
#   Gum::spin "Loading..." "sleep 2"
#
# Theme is controlled by BASHSMITH_GUM_THEME env var (simple, catppuccin, etc.)
# and BASHSMITH_GUM_COLORS env vars for fine-grained overrides.

# Require gum
command -v gum &>/dev/null || {
  echo "gum not found. Install: brew install charmbracelet/tap/gum" >&2
  return 1 2>/dev/null || exit 1
}

# ── Theme ─────────────────────────────────────────────────────────────────────
# Default colors and styles. Override with env vars or per-call flags.
: "${BASHSMITH_GUM_THEME:=simple}"

# Common color palette (ANSI 256 or hex)
_GUM_COLOR_PRIMARY="${BASHSMITH_GUM_COLOR_PRIMARY:-212}"   # Magenta
_GUM_COLOR_SECONDARY="${BASHSMITH_GUM_COLOR_SECONDARY:-57}"  # Cyan
_GUM_COLOR_ACCENT="${BASHSMITH_GUM_COLOR_ACCENT:-99}"        # Violet
_GUM_COLOR_MUTED="${BASHSMITH_GUM_COLOR_MUTED:-240}"       # Gray
_GUM_COLOR_ERROR="${BASHSMITH_GUM_COLOR_ERROR:-196}"       # Red
_GUM_COLOR_SUCCESS="${BASHSMITH_GUM_COLOR_SUCCESS:-82}"    # Green

# ── gum choose ─────────────────────────────────────────────────────────────────

# Gum::choose_single — single selection from a list.
# Arguments: options as separate strings or newline-separated from stdin.
# Returns: selected item via stdout. Exit 1 on Esc/Ctrl+C.
# Usage:
#   choice=$(Gum::choose_single "Deploy" "Rollback" "Cancel")
#   echo "$choice"
Gum::choose_single() {
  gum choose "$@"
}

# Gum::choose_multi — multi-selection from a list.
# Arguments: options as separate strings.
# Returns: newline-separated selections via stdout.
# Usage:
#   selected=$(Gum::choose_multi --no-limit "Server A" "Server B" "Server C")
#   echo "$selected"
Gum::choose_multi() {
  gum choose --no-limit "$@"
}

# Gum::choose_from_file — single selection read from a file (one item per line).
# Arguments: $1 = file path.
# Returns: selected item via stdout.
Gum::choose_from_file() {
  local file="${1:?File required}"
  gum choose < "$file"
}

# Gum::menu_main — main application menu with header.
# Arguments: title, then option pairs (label description).
# Usage:
#   choice=$(Gum::menu_main "My App" "scan:Scan network" "logs:View logs" "quit:Exit")
Gum::menu_main() {
  local title="${1:?Title required}"; shift
  printf '%s\n' "$@" | gum choose --header "$title"
}

# ── gum input ──────────────────────────────────────────────────────────────────

# Gum::input — single-line text input.
# Arguments: standard gum input flags (--placeholder, --value, --password, etc.).
# Returns: user input via stdout.
# Usage:
#   name=$(Gum::input --placeholder "Your name")
#   pass=$(Gum::input --password --placeholder "Password")
Gum::input() {
  gum input "$@"
}

# Gum::input_required — single-line input with non-empty validation loop.
# Arguments: $1 = placeholder text.
# Returns: non-empty user input via stdout.
Gum::input_required() {
  local placeholder="${1:?Placeholder required}"
  local value
  while true; do
    value=$(gum input --placeholder "$placeholder")
    if [[ -n "$value" ]]; then
      echo "$value"
      return 0
    fi
    gum style --foreground "${_GUM_COLOR_ERROR}" "Input cannot be empty. Try again."
  done
}

# Gum::input_with_default — input with a pre-filled default value.
# Arguments: $1 = placeholder, $2 = default value.
Gum::input_with_default() {
  local placeholder="${1:?Placeholder required}"
  local default="${2:-}"
  gum input --placeholder "$placeholder" --value "$default"
}

# ── gum write ──────────────────────────────────────────────────────────────────

# Gum::write — multi-line text input (Ctrl+D to finish).
# Arguments: standard gum write flags.
# Returns: multi-line text via stdout.
# Usage:
#   content=$(Gum::write --placeholder "Enter description...")
Gum::write() {
  gum write "$@"
}

# ── gum spin ───────────────────────────────────────────────────────────────────

# Gum::spin — run a command with a spinner.
# Arguments: $1 = title, $2.. = command and args.
# Returns: command output via stdout.
# Usage:
#   output=$(Gum::spin "Deploying..." deploy.sh --env prod)
#   if [[ $? -eq 0 ]]; then echo "Deployed"; fi
Gum::spin() {
  local title="${1:?Title required}"; shift
  gum spin --title "$title" --spinner dot "$@"
}

# Gum::spin_custom — spinner with custom style.
# Arguments: $1 = title, $2 = spinner style, $3.. = command.
Gum::spin_custom() {
  local title="${1:?Title required}"
  local style="${2:?Spinner style required}"; shift 2
  gum spin --title "$title" --spinner "$style" "$@"
}

# Available spinner styles: line, dot, minidot, jump, pulse, points,
#                          globe, moon, monkey, meter, hamburger

# ── gum confirm ────────────────────────────────────────────────────────────────

# Gum::confirm — yes/no confirmation.
# Arguments: $1 = prompt text.
# Returns: exit 0 (yes) or exit 1 (no).
# Usage:
#   if Gum::confirm "Delete all data?"; then
#     rm -rf /data
#   fi
Gum::confirm() {
  local prompt="${1:?Prompt required}"
  gum confirm "$prompt"
}

# Gum::confirm_destructive — destructive action confirmation with red styling.
# Arguments: $1 = action description.
# Returns: exit 0 (proceed) or exit 1 (abort).
Gum::confirm_destructive() {
  local action="${1:?Action required}"
  gum confirm \
    --affirmative "Delete" \
    --negative "Cancel" \
    "$(gum style --foreground "${_GUM_COLOR_ERROR}" "⚠ Delete: $action")" \
    && return 0 || return 1
}

# ── gum filter ─────────────────────────────────────────────────────────────────

# Gum::filter_single — fuzzy filter returning one selection.
# Arguments: $1 = placeholder, $2.. = items or stdin.
# Returns: selected item via stdout.
# Usage:
#   file=$(Gum::filter_single "Select a file" "${files[@]}")
#   echo "$file" | Gum::filter_single "Search files..."
Gum::filter_single() {
  local placeholder="${1:?Placeholder required}"; shift
  gum filter --limit 1 --placeholder "$placeholder" "$@"
}

# Gum::filter_multi — fuzzy filter with multiple selections.
# Arguments: $1 = placeholder, $2.. = items or stdin.
# Returns: newline-separated selections via stdout.
Gum::filter_multi() {
  local placeholder="${1:?Placeholder required}"; shift
  gum filter --no-limit --placeholder "$placeholder" "$@"
}

# Gum::filter_git_branches — filter git branches for checkout.
# Returns: selected branch name via stdout.
Gum::filter_git_branches() {
  git branch | cut -c 3- | gum filter --limit 1 --placeholder "Switch to branch..."
}

# ── gum table ──────────────────────────────────────────────────────────────────

# Gum::table_csv — render a table from CSV data.
# Arguments: $1 = columns header string, $2 = data file or stdin.
# Returns: selected row via stdout (or --print for all rows).
# Usage:
#   Gum::table_csv "Name,IP,Status" < data.csv
#   row=$(Gum::table_csv "Name,IP,Status" < data.csv)
Gum::table_csv() {
  local columns="${1:?Columns required}"
  gum table --columns "$columns" "$@"
}

# Gum::table_print — render and print all rows without selection.
Gum::table_print() {
  local columns="${1:?Columns required}"
  gum table --columns "$columns" --print "$@"
}

# ── gum style ──────────────────────────────────────────────────────────────────

# Gum::box — wrap text in a styled box.
# Arguments: $1 = text, $2 = foreground color, $3 = border style (default rounded).
# Returns: styled text via stdout.
Gum::box() {
  local text="${1:?Text required}"
  local fg="${2:-${_GUM_COLOR_PRIMARY}}"
  local border="${3:-rounded}"
  gum style --foreground "$fg" \
    --border "$border" \
    --border-foreground "$fg" \
    --padding "1 2" \
    "$text"
}

# Gum::header — styled section header.
Gum::header() {
  local text="${1:?Text required}"
  gum style --bold --foreground "${_GUM_COLOR_PRIMARY}" "══ $text ══"
}

# Gum::success — green success message.
Gum::success() {
  gum style --foreground "${_GUM_COLOR_SUCCESS}" "✓ $*"
}

# Gum::error — red error message.
Gum::error() {
  gum style --foreground "${_GUM_COLOR_ERROR}" "✗ $*"
}

# Gum::info — muted info message.
Gum::info() {
  gum style --foreground "${_GUM_COLOR_MUTED}" "ℹ $*"
}

# ── gum pager ──────────────────────────────────────────────────────────────────

# Gum::pager — scroll through content.
# Arguments: $1 = file or stdin.
# Returns: renders in terminal (no stdout capture).
# Usage:
#   Gum::pager < README.md
#   cat log.txt | Gum::pager
Gum::pager() {
  gum pager "$@"
}

# Gum::pager_with_lines — pager with line numbers.
Gum::pager_with_lines() {
  gum pager --show-line-numbers "$@"
}

# ── gum format ────────────────────────────────────────────────────────────────

# Gum::format_json — pretty-print JSON with jq then color with gum format.
# Arguments: $1 = json string or file.
# Returns: colored output via stdout.
Gum::format_json() {
  local input="${1:--}"
  jq . "$input" | gum format --type json
}

# ── Error handling helpers ─────────────────────────────────────────────────────

# Gum::catch_ctrlc — trap Ctrl+C in gum interactions.
# Usage: Gum::catch_ctrlc; gum choose ...
Gum::catch_ctrlc() {
  trap 'gum style --foreground 196 "Interrupted."; exit 130' INT
}

# Gum::require — exit if gum is not available.
Gum::require() {
  command -v gum &>/dev/null || {
    gum style --foreground "${_GUM_COLOR_ERROR}" \
      "ERROR: gum is required but not installed." \
      "Install: brew install charmbracelet/tap/gum"
    return 1 2>/dev/null || exit 1
  }
}
