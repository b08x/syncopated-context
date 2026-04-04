#!/bin/bash
# =============================================================================
# Project Detection & Analysis Script
# Scans a target directory and outputs a JSON report of detected frameworks,
# services, and dependencies for containerization planning.
#
# Usage: detect_project.sh <project-root>
# Output: JSON to stdout describing detected services and structure
# =============================================================================

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo '{"error": "Directory not found: '"$PROJECT_ROOT"'"}' >&2
  exit 1
fi

cd "$PROJECT_ROOT"

# ---- Helper: check if file contains pattern ----
file_contains() {
  local file="$1" pattern="$2"
  [ -f "$file" ] && grep -qE "$pattern" "$file" 2>/dev/null
}

# ---- Accumulate detected services as JSON fragments ----
SERVICES=()
DATABASES=()
HAS_AI_WORKLOAD="false"
EXISTING_DOCKERFILES=()
EXISTING_COMPOSE="false"

# ---- Scan for existing Docker artifacts ----
scan_existing_docker() {
  while IFS= read -r -d '' df; do
    EXISTING_DOCKERFILES+=("\"$(echo "$df" | sed 's|^\./||')\"")
  done < <(find . -maxdepth 3 -name "Dockerfile*" -print0 2>/dev/null)

  if [ -f "compose.yaml" ] || [ -f "compose.yml" ] || [ -f "docker-compose.yaml" ] || [ -f "docker-compose.yml" ]; then
    EXISTING_COMPOSE="true"
  fi
}

# ---- Ruby / Sinatra Detection ----
detect_ruby() {
  local locations=("." "backend" "api" "server" "services/backend-api" "services/backend")
  for loc in "${locations[@]}"; do
    if [ -f "$loc/Gemfile" ]; then
      local framework="ruby-generic"
      local entry_cmd="ruby app.rb"
      if file_contains "$loc/Gemfile" "sinatra"; then
        framework="sinatra"
        if [ -f "$loc/config.ru" ]; then
          entry_cmd="bundle exec rackup --host 0.0.0.0 -p 4567"
        fi
      elif file_contains "$loc/Gemfile" "rails"; then
        framework="rails"
        entry_cmd="bundle exec rails server -b 0.0.0.0"
      fi
      local has_c_ext="false"
      if file_contains "$loc/Gemfile" "pg\|nokogiri\|ffi\|mysql2\|sqlite3"; then
        has_c_ext="true"
      fi
      SERVICES+=("{\"name\": \"backend-api\", \"type\": \"backend\", \"framework\": \"$framework\", \"language\": \"ruby\", \"location\": \"$loc\", \"entry_cmd\": \"$entry_cmd\", \"has_c_extensions\": $has_c_ext}")
      return
    fi
  done
}

# ---- React / Vite / Node Frontend Detection ----
detect_frontend() {
  local locations=("." "frontend" "client" "web" "services/web-frontend" "services/frontend")
  for loc in "${locations[@]}"; do
    if [ -f "$loc/package.json" ]; then
      local framework="node-generic"
      local build_tool="unknown"

      if file_contains "$loc/package.json" '"vite"'; then
        build_tool="vite"
      elif [ -f "$loc/webpack.config.js" ] || [ -f "$loc/webpack.config.ts" ]; then
        build_tool="webpack"
      elif file_contains "$loc/package.json" '"react-scripts"'; then
        build_tool="cra"
      fi

      if file_contains "$loc/package.json" '"react"'; then
        framework="react"
      elif file_contains "$loc/package.json" '"vue"'; then
        framework="vue"
      elif file_contains "$loc/package.json" '"svelte"'; then
        framework="svelte"
      elif file_contains "$loc/package.json" '"next"'; then
        framework="nextjs"
        build_tool="next"
      fi

      local has_typescript="false"
      if [ -f "$loc/tsconfig.json" ]; then
        has_typescript="true"
      fi

      # Only classify as frontend if it has a build tool or frontend framework
      # Otherwise it might be a Node backend
      if [ "$framework" != "node-generic" ] || [ "$build_tool" != "unknown" ]; then
        SERVICES+=("{\"name\": \"web-frontend\", \"type\": \"frontend\", \"framework\": \"$framework\", \"build_tool\": \"$build_tool\", \"language\": \"typescript\", \"has_typescript\": $has_typescript, \"location\": \"$loc\"}")
        return
      fi
    fi
  done
}

# ---- Node Backend Detection ----
detect_node_backend() {
  local locations=("." "backend" "api" "server" "services/backend-api" "services/backend")
  for loc in "${locations[@]}"; do
    if [ -f "$loc/package.json" ]; then
      local framework="node-generic"
      if file_contains "$loc/package.json" '"express"'; then
        framework="express"
      elif file_contains "$loc/package.json" '"fastify"'; then
        framework="fastify"
      elif file_contains "$loc/package.json" '"@nestjs/core"'; then
        framework="nestjs"
      fi

      # Only if we detected a backend framework (not a frontend)
      if [ "$framework" != "node-generic" ]; then
        SERVICES+=("{\"name\": \"backend-api\", \"type\": \"backend\", \"framework\": \"$framework\", \"language\": \"node\", \"location\": \"$loc\"}")
        return
      fi
    fi
  done
}

# ---- Python Detection (Web vs AI) ----
detect_python() {
  local locations=("." "backend" "api" "server" "ai" "ml" "inference" "worker" "services/backend-api" "services/ai-inference")
  for loc in "${locations[@]}"; do
    local req_file=""
    if [ -f "$loc/requirements.txt" ]; then
      req_file="$loc/requirements.txt"
    elif [ -f "$loc/pyproject.toml" ]; then
      req_file="$loc/pyproject.toml"
    fi

    if [ -n "$req_file" ]; then
      # Check for AI/ML libraries
      if grep -qEi "torch|tensorflow|openvino|chromadb|transformers|langchain|llama.index|sentence.transformers|diffusers|onnxruntime" "$req_file" 2>/dev/null; then
        HAS_AI_WORKLOAD="true"
        local ai_libs=""
        for lib in torch tensorflow openvino chromadb transformers langchain; do
          if grep -qEi "$lib" "$req_file" 2>/dev/null; then
            ai_libs="${ai_libs:+$ai_libs, }$lib"
          fi
        done
        SERVICES+=("{\"name\": \"ai-inference\", \"type\": \"ai-worker\", \"framework\": \"python-ai\", \"language\": \"python\", \"location\": \"$loc\", \"ai_libraries\": \"$ai_libs\"}")
      fi

      # Check for web frameworks
      if grep -qEi "flask|django|fastapi|uvicorn|gunicorn" "$req_file" 2>/dev/null; then
        local py_framework="python-web"
        local py_cmd="python app.py"
        if grep -qEi "flask" "$req_file" 2>/dev/null; then
          py_framework="flask"
          py_cmd="gunicorn --bind 0.0.0.0:5000 app:app"
        elif grep -qEi "fastapi" "$req_file" 2>/dev/null; then
          py_framework="fastapi"
          py_cmd="uvicorn main:app --host 0.0.0.0 --port 8000"
        elif grep -qEi "django" "$req_file" 2>/dev/null; then
          py_framework="django"
          py_cmd="gunicorn --bind 0.0.0.0:8000 config.wsgi:application"
        fi
        # Only add if we haven't already added a backend from Ruby/Node
        local already_has_backend="false"
        for svc in "${SERVICES[@]}"; do
          if echo "$svc" | grep -q '"type": "backend"'; then
            already_has_backend="true"
            break
          fi
        done
        if [ "$already_has_backend" = "false" ]; then
          SERVICES+=("{\"name\": \"backend-api\", \"type\": \"backend\", \"framework\": \"$py_framework\", \"language\": \"python\", \"location\": \"$loc\", \"entry_cmd\": \"$py_cmd\"}")
        fi
      fi
    fi
  done
}

# ---- Database Detection ----
detect_databases() {
  # Check for SQL init files
  if find . -maxdepth 2 -name "*.sql" -print -quit 2>/dev/null | grep -q .; then
    if grep -rlq "vector" ./*.sql ./infra/**/*.sql 2>/dev/null; then
      DATABASES+=("{\"name\": \"postgres-vector\", \"type\": \"pgvector\", \"image\": \"pgvector/pgvector:pg16\"}")
    else
      DATABASES+=("{\"name\": \"postgres\", \"type\": \"postgresql\", \"image\": \"postgres:16-alpine\"}")
    fi
  fi

  # Check compose/env/code for database references
  local search_files=$(find . -maxdepth 2 \( -name "*.yaml" -o -name "*.yml" -o -name "*.env*" -o -name "*.py" -o -name "*.rb" -o -name "*.js" -o -name "*.ts" \) 2>/dev/null)
  if echo "$search_files" | xargs grep -lq "chromadb\|chroma" 2>/dev/null; then
    DATABASES+=("{\"name\": \"chromadb\", \"type\": \"vector-db\", \"image\": \"chromadb/chroma:latest\"}")
  fi
  if echo "$search_files" | xargs grep -lq "falkordb\|falkor" 2>/dev/null; then
    DATABASES+=("{\"name\": \"falkordb\", \"type\": \"graph-db\", \"image\": \"falkordb/falkordb-server:latest\"}")
  fi
  if echo "$search_files" | xargs grep -lq "redis" 2>/dev/null; then
    # Don't double-count if FalkorDB already detected (it's Redis-based)
    local has_falkor="false"
    for db in "${DATABASES[@]}"; do
      if echo "$db" | grep -q "falkordb"; then has_falkor="true"; break; fi
    done
    if [ "$has_falkor" = "false" ]; then
      DATABASES+=("{\"name\": \"redis-cache\", \"type\": \"cache\", \"image\": \"redis:7-alpine\"}")
    fi
  fi
}

# ---- Check directory structure ----
detect_structure() {
  local structure="flat"
  if [ -d "services" ]; then
    structure="microservices"
  elif [ -d "frontend" ] && ([ -d "backend" ] || [ -d "api" ]); then
    structure="split"
  fi
  echo "$structure"
}

# ---- Execute Detection ----
scan_existing_docker
detect_frontend
detect_ruby
detect_node_backend
detect_python
detect_databases

STRUCTURE=$(detect_structure)

# ---- Build JSON Output ----
join_array() {
  local arr=("$@")
  local result=""
  for item in "${arr[@]}"; do
    result="${result:+$result, }$item"
  done
  echo "$result"
}

SERVICES_JSON=$(join_array "${SERVICES[@]+"${SERVICES[@]}"}")
DATABASES_JSON=$(join_array "${DATABASES[@]+"${DATABASES[@]}"}")
DOCKERFILES_JSON=$(join_array "${EXISTING_DOCKERFILES[@]+"${EXISTING_DOCKERFILES[@]}"}")

cat <<EOF
{
  "project_root": "$(pwd)",
  "current_structure": "$STRUCTURE",
  "has_ai_workload": $HAS_AI_WORKLOAD,
  "existing_docker": {
    "has_compose": $EXISTING_COMPOSE,
    "dockerfiles": [${DOCKERFILES_JSON}]
  },
  "detected_services": [${SERVICES_JSON}],
  "detected_databases": [${DATABASES_JSON}],
  "service_count": ${#SERVICES[@]},
  "recommended_profiles": $(if [ "$HAS_AI_WORKLOAD" = "true" ]; then echo '["cpu", "nvidia", "intel"]'; else echo '["cpu", "nvidia", "intel"]'; fi)
}
EOF
