#!/usr/bin/env bash
# lib/bootstrap.sh — Robust system detection, dependency checking, and environment setup.
# This library provides reusable functions for bootstrapping Bashsmith projects.
#
# Usage:
#   source lib/bootstrap.sh
#   Bootstrap::detect_os
#   Bootstrap::check_git
#   Bootstrap::install_uv
#   Bootstrap::check_python "3.11"
#   Bootstrap::check_node "22"
#   Bootstrap::setup_path "$HOME/.local/bin"

# ── Colors & Logging ──────────────────────────────────────────────────────────
: "${BASHSMITH_RED:=\033[0;31m}"
: "${BASHSMITH_GREEN:=\033[0;32m}"
: "${BASHSMITH_YELLOW:=\033[0;33m}"
: "${BASHSMITH_BLUE:=\033[0;34m}"
: "${BASHSMITH_MAGENTA:=\033[0;35m}"
: "${BASHSMITH_CYAN:=\033[0;36m}"
: "${BASHSMITH_NC:=\033[0m}"
: "${BASHSMITH_BOLD:=\033[1m}"

Bootstrap::log_info()    { echo -e "${BASHSMITH_CYAN}→${BASHSMITH_NC} $*"; }
Bootstrap::log_success() { echo -e "${BASHSMITH_GREEN}✓${BASHSMITH_NC} $*"; }
Bootstrap::log_warn()    { echo -e "${BASHSMITH_YELLOW}⚠${BASHSMITH_NC} $*"; }
Bootstrap::log_error()   { echo -e "${BASHSMITH_RED}✗${BASHSMITH_NC} $*"; }

# ── System Detection ──────────────────────────────────────────────────────────
Bootstrap::detect_os() {
  case "$(uname -s)" in
    Linux*)
      OS="linux"
      if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        DISTRO="$ID"
      else
        DISTRO="unknown"
      fi
      ;;
    Darwin*)
      OS="macos"
      DISTRO="macos"
      ;;
    CYGWIN*|MINGW*|MSYS*)
      OS="windows"
      DISTRO="windows"
      ;;
    *)
      OS="unknown"
      DISTRO="unknown"
      ;;
  esac
  export OS DISTRO
  Bootstrap::log_success "Detected: $OS ($DISTRO)"
}

# ── Dependency Checks ─────────────────────────────────────────────────────────

Bootstrap::check_git() {
  Bootstrap::log_info "Checking Git..."
  if command -v git &>/dev/null; then
    Bootstrap::log_success "Git $(git --version | awk '{print $3}') found"
    return 0
  fi
  Bootstrap::log_error "Git not found."
  return 1
}

Bootstrap::install_uv() {
  Bootstrap::log_info "Checking for uv package manager..."
  if command -v uv &>/dev/null; then
    Bootstrap::log_success "uv found ($($(command -v uv) --version))"
    return 0
  fi

  Bootstrap::log_info "Installing uv (fast Python package manager)..."
  if curl -LsSf https://astral.sh/uv/install.sh | sh; then
    # Reload path to find uv
    # shellcheck source=/dev/null
    [[ -f "$HOME/.local/bin/env" ]] && . "$HOME/.local/bin/env"
    if command -v uv &>/dev/null; then
      Bootstrap::log_success "uv installed ($($(command -v uv) --version))"
      return 0
    fi
  fi
  Bootstrap::log_error "Failed to install uv."
  return 1
}

Bootstrap::check_python() {
  local version="${1:-3.11}"
  Bootstrap::log_info "Checking Python $version..."
  
  if ! command -v uv &>/dev/null; then
    Bootstrap::log_error "uv not found. Install uv first."
    return 1
  fi

  if uv python find "$version" &>/dev/null; then
    Bootstrap::log_success "Python $version found"
    return 0
  fi

  Bootstrap::log_info "Python $version not found, installing via uv..."
  if uv python install "$version"; then
    Bootstrap::log_success "Python $version installed"
    return 0
  fi
  Bootstrap::log_error "Failed to install Python $version."
  return 1
}

Bootstrap::check_node() {
  local version="${1:-22}"
  Bootstrap::log_info "Checking Node.js $version..."
  if command -v node &>/dev/null; then
    local current_ver
    current_ver=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [[ "$current_ver" -ge "$version" ]]; then
      Bootstrap::log_success "Node.js $(node -v) found"
      return 0
    fi
  fi
  Bootstrap::log_warn "Node.js $version+ not found."
  return 1
}

# ── Environment Setup ─────────────────────────────────────────────────────────

Bootstrap::setup_path() {
  local target_dir="${1:-$HOME/.local/bin}"
  Bootstrap::log_info "Setting up PATH for $target_dir..."

  if echo "$PATH" | tr ':' '\n' | grep -q "^$target_dir$"; then
    Bootstrap::log_info "$target_dir already on PATH"
    return 0
  fi

  local shell_config=""
  case "$(basename "$SHELL")" in
    zsh)  shell_config="$HOME/.zshrc" ;;
    bash) shell_config="$HOME/.bashrc" ;;
    *)    shell_config="$HOME/.profile" ;;
  esac

  if [[ -f "$shell_config" ]]; then
    if ! grep -q "$target_dir" "$shell_config"; then
      echo -e "\n# Added by Bootstrap\nexport PATH=\"$target_dir:\$PATH\"" >> "$shell_config"
      Bootstrap::log_success "Added $target_dir to $shell_config"
      Bootstrap::log_info "Run 'source $shell_config' to update current session"
    fi
  fi
}
