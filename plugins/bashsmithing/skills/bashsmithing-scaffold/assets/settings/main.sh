#!/usr/bin/env bash
# settings/main.sh — Global settings for Bashsmith projects.
# All bin/* scripts should source this file first.
#
# Strict mode is enabled immediately so all sourced files inherit it.
# This cannot be deferred — state must be safe from the first line.

# ── Strict mode ────────────────────────────────────────────────────────────────
# Exit immediately if a command fails.
set -o errexit

# Treat unset variables as errors (use ${var:-default} to provide fallbacks).
set -o nounset

# Propagate non-zero exit codes through pipe chains.
set -o pipefail

# Define newlines and tabs as word delimiters (not spaces).
IFS=$'\n\t'

# ── Paths ─────────────────────────────────────────────────────────────────────
# Project root — derived from the location of this settings file.
export BASHSMITH_ROOT="${BASHSMITH_ROOT:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)}"

# Library path — where lib/*.sh files live.
export BASHSMITH_LIB="${BASHSMITH_LIB:-${BASHSMITH_ROOT}/lib}"

# Settings path — where settings/*.sh files live.
export BASHSMITH_SETTINGS="${BASHSMITH_SETTINGS:-${BASHSMITH_ROOT}/settings}"

# ── Monad library ───────────────────────────────────────────────────────────────
# Always source the Return monad library if it exists.
# This makes Return::success and Return::failure available everywhere.
if [[ -f "${BASHSMITH_LIB}/monad.sh" ]]; then
  # shellcheck source=/dev/null
  source "${BASHSMITH_LIB}/monad.sh"
fi

# ── Logging ───────────────────────────────────────────────────────────────────
# Log level: DEBUG | INFO | WARN | ERROR (default INFO).
export BASHSMITH_LOG_LEVEL="${BASHSMITH_LOG_LEVEL:-INFO}"

# Log format: TIMESTAMP LEVEL PID MSG (ISO 8601 timestamps).
export BASHSMITH_LOG_FORMAT="${BASHSMITH_LOG_FORMAT:-TIMESTAMP LEVEL PID MSG}"

# Log to syslog (1) or stderr (0). Default stderr for interactive scripts.
export BASHSMITH_LOG_SYSLOG="${BASHSMITH_LOG_SYSLOG:-0}"

# ── Shellcheck ────────────────────────────────────────────────────────────────
# Additional shellcheck codes to disable (comma-separated).
# Applied via SHELLCHECK_OPTS environment variable.
export SHELLCHECK_OPTS="${SHELLCHECK_OPTS---exclude=SC1090,SC1091,SC2034,SC2086,SC2317}"

# ── Gum (TUI) ───────────────────────────────────────────────────────────────
# Gum binary path — leave empty to use $PATH.
export BASHSMITH_GUM_PATH="${BASHSMITH_GUM_PATH:-}"

# Gum theme: simple, base16, catppuccin, Dracula, fourk (default simple).
export BASHSMITH_GUM_THEME="${BASHSMITH_GUM_THEME:-simple}"

# ── Debugging ────────────────────────────────────────────────────────────────
# Enable xtrace (set -x) for verbose debugging.
# Toggle with: BASHSMITH_DEBUG=1 ./bin/run ...
export BASHSMITH_DEBUG="${BASHSMITH_DEBUG:-0}"

if [[ "${BASHSMITH_DEBUG}" == "1" ]]; then
  set -o xtrace
fi
