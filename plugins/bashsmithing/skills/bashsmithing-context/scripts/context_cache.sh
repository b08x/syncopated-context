#!/usr/bin/env bash
# scripts/context_cache.sh — JSON cache for CLI tool documentation.
# Replaces SQLite from the Ruby version with a pure jq/bash implementation.

set -euo pipefail
IFS=$'\n\t'

CACHE_DIR="${HOME}/.bashsmithing"
CACHE_FILE="${CACHE_DIR}/context_cache.json"

# Ensure cache directory and file exist
mkdir -p "$CACHE_DIR"
if [[ ! -f "$CACHE_FILE" ]]; then
  echo '{"tools":{}}' > "$CACHE_FILE"
fi

# Acquire exclusive lock to prevent race conditions during concurrent accesses
exec 9> "${CACHE_FILE}.lock"
flock 9

# Helper: current time in seconds since epoch
_now() {
  date +%s
}

# ── store ───────────────────────────────────────────────────────────────────────
cmd_store() {
  local tool="${1:?Tool name required}"
  local url="${2:-}"
  local flags_json="${3:-[]}"
  local examples_json="${4:-[]}"
  local ttl_days="${5:-30}"

  local resolved_at
  resolved_at=$(_now)

  # Update the JSON using jq
  local tmp
  tmp=$(mktemp)
  jq --arg tool "$tool" \
     --arg url "$url" \
     --argjson flags "$flags_json" \
     --argjson examples "$examples_json" \
     --arg resolved_at "$resolved_at" \
     --arg ttl "$ttl_days" \
     '.tools[$tool] = {
       "url": $url,
       "flags": $flags,
       "examples": $examples,
       "resolved_at": ($resolved_at | tonumber),
       "ttl_days": ($ttl | tonumber)
     }' "$CACHE_FILE" > "$tmp"
  
  mv "$tmp" "$CACHE_FILE"
  echo "Stored: $tool"
}

# ── fetch / stale ───────────────────────────────────────────────────────────────
_fetch_internal() {
  local tool="$1"
  local allow_stale="$2"
  local as_json="$3"

  if ! jq -e --arg tool "$tool" '.tools | has($tool)' "$CACHE_FILE" >/dev/null; then
    [[ "$as_json" == "1" ]] && echo '{"status":"miss"}' || echo "Miss: $tool"
    return 1
  fi

  local entry
  entry=$(jq -c --arg tool "$tool" '.tools[$tool]' "$CACHE_FILE")
  
  local resolved_at ttl_days now age_days age_seconds ttl_seconds
  resolved_at=$(jq -r '.resolved_at' <<< "$entry")
  ttl_days=$(jq -r '.ttl_days' <<< "$entry")
  now=$(_now)
  
  age_seconds=$(( now - resolved_at ))
  age_days=$(( age_seconds / 86400 ))
  ttl_seconds=$(( ttl_days * 86400 ))

  local status="fresh"
  local exit_code=0

  if (( age_seconds > ttl_seconds )); then
    if [[ "$allow_stale" == "1" ]]; then
      status="stale"
      exit_code=2
    else
      [[ "$as_json" == "1" ]] && echo '{"status":"miss"}' || echo "Miss (expired): $tool"
      return 1
    fi
  fi

  if [[ "$as_json" == "1" ]]; then
    local warning=""
    if [[ "$status" == "stale" ]]; then
      warning="# [WARNING: Stale CLI Syntax]\n# Documentation cache for $tool is expired.\n# Verify against official sources before use."
    fi
    
    jq -c --arg status "$status" \
       --arg tool "$tool" \
       --arg age "$age_days" \
       --arg warning "$warning" \
       '. + {
         "status": $status,
         "tool_name": $tool,
         "age_days": ($age | tonumber),
         "warning": $warning
       }' <<< "$entry"
  else
    echo "Status: $status"
    echo "Tool: $tool"
    echo "URL: $(jq -r '.url' <<< "$entry")"
    echo "Age: $age_days days (TTL: $ttl_days days)"
    if [[ "$status" == "stale" ]]; then
      echo "WARNING: Cache is stale."
    fi
    echo "Flags: $(jq -r '.flags | join(", ")' <<< "$entry")"
    echo "Examples: $(jq -r '.examples | join(" | ")' <<< "$entry")"
  fi

  return "$exit_code"
}

cmd_fetch() {
  local tool="${1:?Tool name required}"
  local as_json=0
  [[ "${2:-}" == "--json" ]] && as_json=1
  _fetch_internal "$tool" 0 "$as_json"
}

cmd_stale() {
  local tool="${1:?Tool name required}"
  local as_json=0
  [[ "${2:-}" == "--json" ]] && as_json=1
  _fetch_internal "$tool" 1 "$as_json"
}

# ── list ───────────────────────────────────────────────────────────────────────
cmd_list() {
  local as_json=0
  [[ "${1:-}" == "--json" ]] && as_json=1

  if [[ "$as_json" == "1" ]]; then
    jq -c '.tools' "$CACHE_FILE"
  else
    echo "Cached tools:"
    jq -r '.tools | keys[]' "$CACHE_FILE" | while read -r tool; do
      local resolved_at ttl_days now age_seconds age_days
      resolved_at=$(jq -r --arg tool "$tool" '.tools[$tool].resolved_at' "$CACHE_FILE")
      ttl_days=$(jq -r --arg tool "$tool" '.tools[$tool].ttl_days' "$CACHE_FILE")
      now=$(_now)
      age_seconds=$(( now - resolved_at ))
      age_days=$(( age_seconds / 86400 ))
      
      local status="fresh"
      (( age_seconds > (ttl_days * 86400) )) && status="stale"
      
      printf "  %-15s (%s, age: %d days, ttl: %d days)\n" "$tool" "$status" "$age_days" "$ttl_days"
    done
  fi
}

# ── evict ──────────────────────────────────────────────────────────────────────
cmd_evict() {
  local tool="${1:?Tool name required}"
  local tmp
  tmp=$(mktemp)
  jq --arg tool "$tool" 'del(.tools[$tool])' "$CACHE_FILE" > "$tmp"
  mv "$tmp" "$CACHE_FILE"
  echo "Evicted: $tool"
}

# ── Main ───────────────────────────────────────────────────────────────────────
action="${1:-list}"
shift || true

case "$action" in
  store) cmd_store "$@" ;;
  fetch|check) cmd_fetch "$@" ;;
  stale) cmd_stale "$@" ;;
  list) cmd_list "$@" ;;
  evict) cmd_evict "$@" ;;
  *)
    echo "Usage: $0 {store|fetch|stale|list|evict} ..." >&2
    exit 1
    ;;
esac
