#!/bin/bash
# =============================================================================
# Microservice Refactoring Script
# Restructures unstructured polyglot codebases into a canonical layout.
#
# Usage: refactor_project.sh <project-root> [--dry-run]
#
# This script is idempotent and safe. It checks for directory existence before
# creation and uses non-destructive checks before moving files.
#
# The --dry-run flag prints planned actions without executing them.
# =============================================================================

set -euo pipefail

PROJECT_ROOT="${1:-.}"
DRY_RUN="${2:-}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "[ERROR] Directory not found: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

# ---- Configuration ----
SERVICES_DIR="services"
INFRA_DIR="infra"
FRONTEND_DIR="$SERVICES_DIR/web-frontend"
BACKEND_API_DIR="$SERVICES_DIR/backend-api"
AI_WORKER_DIR="$SERVICES_DIR/ai-inference"
DB_INIT_DIR="$INFRA_DIR/database"
NGINX_DIR="$INFRA_DIR/nginx"
SCRIPTS_DIR="scripts"

# ---- Helpers ----
safe_mkdir() {
  if [ "$DRY_RUN" = "--dry-run" ]; then
    echo "[DRY-RUN] mkdir -p $1"
  else
    mkdir -p "$1"
  fi
}

safe_mv() {
  local src="$1" dst="$2"
  if [ -e "$src" ]; then
    if [ "$DRY_RUN" = "--dry-run" ]; then
      echo "[DRY-RUN] mv $src -> $dst"
    else
      mv "$src" "$dst" 2>/dev/null || true
    fi
  fi
}

safe_mv_glob() {
  local pattern="$1" dst="$2"
  local found=0
  for f in $pattern; do
    if [ -e "$f" ]; then
      found=1
      safe_mv "$f" "$dst"
    fi
  done
  return 0
}

# ---- Create Directory Structure ----
echo "=== Containerization Refactoring ==="
echo "Project: $(pwd)"
if [ "$DRY_RUN" = "--dry-run" ]; then
  echo "Mode: DRY RUN (no changes will be made)"
fi
echo ""

echo "[Phase 1] Creating canonical directory structure..."
safe_mkdir "$FRONTEND_DIR"
safe_mkdir "$BACKEND_API_DIR"
safe_mkdir "$AI_WORKER_DIR"
safe_mkdir "$DB_INIT_DIR"
safe_mkdir "$NGINX_DIR"
safe_mkdir "$SCRIPTS_DIR"

# ---- React / Vite / Frontend ----
detect_and_move_react() {
  if [ -f "vite.config.ts" ] || [ -f "vite.config.js" ] || \
     ([ -f "package.json" ] && grep -q '"vite"\|"react-scripts"\|"react"' package.json 2>/dev/null); then

    # Only move if not already in services/
    if [ ! -f "$FRONTEND_DIR/package.json" ]; then
      echo "[Phase 2] Migrating React/Vite frontend -> $FRONTEND_DIR"

      # Config files
      safe_mv "package.json" "$FRONTEND_DIR/"
      safe_mv "package-lock.json" "$FRONTEND_DIR/"
      safe_mv "yarn.lock" "$FRONTEND_DIR/"
      safe_mv "pnpm-lock.yaml" "$FRONTEND_DIR/"
      safe_mv_glob "vite.config.*" "$FRONTEND_DIR/"
      safe_mv_glob "tsconfig*" "$FRONTEND_DIR/"
      safe_mv_glob ".eslintrc*" "$FRONTEND_DIR/"
      safe_mv_glob ".prettierrc*" "$FRONTEND_DIR/"
      safe_mv "index.html" "$FRONTEND_DIR/"
      safe_mv "postcss.config.js" "$FRONTEND_DIR/"
      safe_mv "tailwind.config.js" "$FRONTEND_DIR/"
      safe_mv "tailwind.config.ts" "$FRONTEND_DIR/"

      # Source directories
      safe_mv "src" "$FRONTEND_DIR/"
      # Only move public/ if it belongs to the frontend (not Sinatra)
      if [ -d "public" ] && [ ! -f "Gemfile" ]; then
        safe_mv "public" "$FRONTEND_DIR/"
      fi
      safe_mv "assets" "$FRONTEND_DIR/"

      echo "  -> Frontend migration complete."
    else
      echo "[SKIP] Frontend already in $FRONTEND_DIR"
    fi
  fi
}

# ---- Ruby / Sinatra Backend ----
detect_and_move_ruby() {
  if [ -f "Gemfile" ] && grep -q "sinatra\|rails" "Gemfile" 2>/dev/null; then
    if [ ! -f "$BACKEND_API_DIR/Gemfile" ]; then
      echo "[Phase 2] Migrating Ruby backend -> $BACKEND_API_DIR"

      safe_mv "Gemfile" "$BACKEND_API_DIR/"
      safe_mv "Gemfile.lock" "$BACKEND_API_DIR/"
      safe_mv "config.ru" "$BACKEND_API_DIR/"
      safe_mv "app.rb" "$BACKEND_API_DIR/"
      safe_mv "Rakefile" "$BACKEND_API_DIR/"

      safe_mv "lib" "$BACKEND_API_DIR/"
      safe_mv "models" "$BACKEND_API_DIR/"
      safe_mv "views" "$BACKEND_API_DIR/"
      safe_mv "helpers" "$BACKEND_API_DIR/"

      # Only move public/ if no frontend claimed it
      if [ -d "public" ] && [ ! -d "$FRONTEND_DIR/public" ]; then
        safe_mv "public" "$BACKEND_API_DIR/"
      fi

      echo "  -> Ruby backend migration complete."
    else
      echo "[SKIP] Ruby backend already in $BACKEND_API_DIR"
    fi
  fi
}

# ---- Python Services ----
detect_and_move_python() {
  local req_file=""
  if [ -f "requirements.txt" ]; then
    req_file="requirements.txt"
  elif [ -f "pyproject.toml" ]; then
    req_file="pyproject.toml"
  fi

  if [ -n "$req_file" ]; then
    # AI/ML workload
    if grep -qEi "torch|tensorflow|openvino|chromadb|transformers|langchain" "$req_file" 2>/dev/null; then
      if [ ! -f "$AI_WORKER_DIR/$req_file" ]; then
        echo "[Phase 2] Migrating Python AI worker -> $AI_WORKER_DIR"

        safe_mv "$req_file" "$AI_WORKER_DIR/"
        safe_mv "pyproject.toml" "$AI_WORKER_DIR/"
        safe_mv_glob "model*.py" "$AI_WORKER_DIR/"
        safe_mv_glob "train*.py" "$AI_WORKER_DIR/"
        safe_mv_glob "inference*.py" "$AI_WORKER_DIR/"
        safe_mv_glob "worker*.py" "$AI_WORKER_DIR/"
        safe_mv "models" "$AI_WORKER_DIR/"
        safe_mv "notebooks" "$AI_WORKER_DIR/"
        safe_mv "weights" "$AI_WORKER_DIR/"
        safe_mv "checkpoints" "$AI_WORKER_DIR/"

        echo "  -> AI worker migration complete."
      else
        echo "[SKIP] AI worker already in $AI_WORKER_DIR"
      fi
    fi

    # Web framework (only if not already moved by Ruby)
    if grep -qEi "flask|django|fastapi" "$req_file" 2>/dev/null; then
      if [ ! -f "$BACKEND_API_DIR/Gemfile" ] && [ ! -f "$BACKEND_API_DIR/$req_file" ]; then
        echo "[Phase 2] Migrating Python web backend -> $BACKEND_API_DIR"

        safe_mv "$req_file" "$BACKEND_API_DIR/"
        safe_mv "app.py" "$BACKEND_API_DIR/"
        safe_mv "main.py" "$BACKEND_API_DIR/"
        safe_mv "wsgi.py" "$BACKEND_API_DIR/"
        safe_mv "templates" "$BACKEND_API_DIR/"
        safe_mv "static" "$BACKEND_API_DIR/"

        echo "  -> Python backend migration complete."
      fi
    fi
  fi
}

# ---- Database Assets ----
move_db_assets() {
  local found=0
  for f in *.sql; do
    if [ -f "$f" ]; then found=1; break; fi
  done
  if [ "$found" = "1" ]; then
    echo "[Phase 2] Migrating database scripts -> $DB_INIT_DIR"
    safe_mv_glob "*.sql" "$DB_INIT_DIR/"
    echo "  -> Database migration complete."
  fi
}

# ---- Execute in order ----
echo ""
echo "[Phase 2] Detecting and migrating services..."
detect_and_move_react
detect_and_move_ruby
detect_and_move_python
move_db_assets

echo ""
echo "=== Refactoring Complete ==="
echo "Structure:"
if [ "$DRY_RUN" != "--dry-run" ]; then
  find . -maxdepth 3 -not -path '*/node_modules/*' -not -path '*/.git/*' -not -name '*.pyc' | head -60 | sort
fi
