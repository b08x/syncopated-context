#!/usr/bin/env bash
# scripts/scaffold.sh — Copies static assets to bootstrap a new bashsmithing project.
# Invoked by the bashsmithing-scaffold skill after gathering project info.
#
# Usage:
#   bash scaffold.sh --name <project-name> --namespace <Namespace> \
#                    --output <dir> --mode <minimal|full>
#
# Outputs key=value pairs to stdout so the caller can capture and verify them.

set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="${SCRIPT_DIR}/../assets"

# ── Helpers ───────────────────────────────────────────────────────────────────
_info()  { printf '  \033[1;34m%s\033[0m\n' "$*"; }
_ok()    { printf '  \033[1;32m✓ %s\033[0m\n' "$*"; }
_error() { printf '  \033[1;31m✗ %s\033[0m\n' "$*" >&2; }

# ── Argument parsing ───────────────────────────────────────────────────────────
PROJECT_NAME=""
NAMESPACE=""
OUTPUT_DIR=""
MODE="minimal"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)      PROJECT_NAME="$2"; shift 2 ;;
    --namespace) NAMESPACE="$2";    shift 2 ;;
    --output)    OUTPUT_DIR="$2";   shift 2 ;;
    --mode)      MODE="$2";         shift 2 ;;
    *) _error "Unknown option: $1"; exit 1 ;;
  esac
done

# ── Validate ──────────────────────────────────────────────────────────────────
[[ -z "$PROJECT_NAME" ]] && { _error "--name is required"; exit 1; }
[[ -z "$NAMESPACE"    ]] && { _error "--namespace is required"; exit 1; }
[[ -z "$OUTPUT_DIR"   ]] && OUTPUT_DIR="./${PROJECT_NAME}"

if [[ "$MODE" != "minimal" && "$MODE" != "full" ]]; then
  _error "--mode must be 'minimal' or 'full'"
  exit 1
fi

if [[ ! -d "$ASSETS_DIR" ]]; then
  _error "Assets directory not found: $ASSETS_DIR"
  exit 1
fi

# ── Directory structure ────────────────────────────────────────────────────────
_info "Creating project structure at ${OUTPUT_DIR}..."
mkdir -p "${OUTPUT_DIR}/bin"
mkdir -p "${OUTPUT_DIR}/lib"
mkdir -p "${OUTPUT_DIR}/settings"
mkdir -p "${OUTPUT_DIR}/bats"
_ok "Directories created"

# ── Copy static assets ─────────────────────────────────────────────────────────
_info "Copying static assets (mode: ${MODE})..."

cp "${ASSETS_DIR}/lib/monad.sh"      "${OUTPUT_DIR}/lib/monad.sh"
cp "${ASSETS_DIR}/lib/cli.sh"        "${OUTPUT_DIR}/lib/cli.sh"
cp "${ASSETS_DIR}/lib/bootstrap.sh"  "${OUTPUT_DIR}/lib/bootstrap.sh"
cp "${ASSETS_DIR}/settings/main.sh"  "${OUTPUT_DIR}/settings/main.sh"
cp "${ASSETS_DIR}/bin/qa"            "${OUTPUT_DIR}/bin/qa"
cp "${ASSETS_DIR}/bin/setup"         "${OUTPUT_DIR}/bin/setup"
cp "${ASSETS_DIR}/.shellcheckrc"     "${OUTPUT_DIR}/.shellcheckrc"

if [[ "$MODE" == "full" ]]; then
  cp "${ASSETS_DIR}/lib/gum.sh" "${OUTPUT_DIR}/lib/gum.sh"
  _ok "Copied: lib/gum.sh (TUI adapter)"
fi

# ── Permissions ───────────────────────────────────────────────────────────────
chmod +x "${OUTPUT_DIR}/bin/qa"
chmod +x "${OUTPUT_DIR}/bin/setup"
_ok "Static assets copied and permissions set"

# ── Output vars for caller ────────────────────────────────────────────────────
# These are captured by the skill to drive the generation step.
printf 'PROJECT_NAME=%s\n' "$PROJECT_NAME"
printf 'NAMESPACE=%s\n'    "$NAMESPACE"
printf 'OUTPUT_DIR=%s\n'   "$OUTPUT_DIR"
printf 'MODE=%s\n'         "$MODE"
