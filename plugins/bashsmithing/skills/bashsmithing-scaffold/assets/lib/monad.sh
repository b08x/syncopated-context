#!/usr/bin/env bash
# lib/monad.sh — Structured return monads for Bashsmith projects.
# Provides Return::success and Return::failure functions that emit strict JSON.
# All scripts should source this file and use these functions instead of bare `return`.
#
# Usage:
#   source lib/monad.sh
#   Return::success "data"          # emits: {"status":"ok","data":"data"}
#   Return::failure "error message" # emits: {"status":"error","message":"error message"}
#
# Unwrapping with jq:
#   result=$(some_function)
#   if   jq -e '.status == "ok"'    <<< "$result" &>/dev/null; then
#     data=$(jq -r '.data'          <<< "$result")
#   else
#     msg=$(jq -r '.message'         <<< "$result")
#   fi

# Namespace delimiter — change if your project uses a different separator.
export BASHSMITH_NAMESPACE_DELIMITER="::"

# ── Return::success ────────────────────────────────────────────────────────────
# Emits a strict JSON object indicating successful execution.
# Arguments:
#   $1 — the data payload (string, number, JSON, or empty)
# stdout: JSON string {"status":"ok","data":<value>}
Return::success() {
  local data="${1:-null}"
  local type
  type=$(Return::_detect_type "$data")

  if [[ "$type" == "string" ]]; then
    # Escape special characters and wrap in double quotes
    local escaped
    escaped=$(Return::_escape_json_string "$data")
    printf '{"status":"ok","data":"%s"}\n' "$escaped"
  elif [[ "$type" == "json" ]]; then
    # Already valid JSON — pass through directly
    printf '{"status":"ok","data":%s}\n' "$data"
  elif [[ "$type" == "null" ]]; then
    printf '{"status":"ok","data":null}\n'
  else
    # Numbers — pass through unquoted
    printf '{"status":"ok","data":%s}\n' "$data"
  fi
}

# ── Return::failure ───────────────────────────────────────────────────────────
# Emits a strict JSON object indicating failure.
# Arguments:
#   $1 — the error message (required)
#   $2 — optional error code (integer, defaults to 1)
# stdout: JSON string {"status":"error","message":"...","code":N}
Return::failure() {
  local message="$1"
  local code="${2:-1}"
  local escaped
  escaped=$(Return::_escape_json_string "$message")

  printf '{"status":"error","message":"%s","code":%d}\n' "$escaped" "$code"
}

# ── Return::unwrap ────────────────────────────────────────────────────────────
# Unwraps a Return monad and sets shell variables from the result.
# Arguments:
#   $1 — the Return JSON string
#   $2 — variable name to store .data or .message
#   $3 — variable name to store exit status (0=ok, 1=error)
# Sets variables in CALLER's scope via eval.
# Usage:
#   Return::unwrap "$(my_function)" "value" "ok"
#   if [[ "$ok" == "0" ]]; then echo "Got: $value"; fi
Return::unwrap() {
  local json="$1"
  local data_var="$2"
  local status_var="$3"

  # Sanitize variable names to prevent arbitrary code execution via eval
  if [[ ! "$data_var" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
    Return::failure "Invalid variable name: $data_var"
    return 1
  fi
  if [[ ! "$status_var" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
    Return::failure "Invalid variable name: $status_var"
    return 1
  fi

  local status
  status=$(jq -r '.status' <<< "$json" 2>/dev/null) || {
    eval "${data_var}='null'"
    eval "${status_var}=1"
    return 1
  }

  if [[ "$status" == "ok" ]]; then
    eval "${data_var}=$(jq -r '.data' <<< "$json" 2>/dev/null | Return::_json_quote)"
    eval "${status_var}=0"
  else
    eval "${data_var}=$(jq -r '.message' <<< "$json" 2>/dev/null | Return::_json_quote)"
    eval "${status_var}=1"
  fi
}

# ── Return::is_ok ─────────────────────────────────────────────────────────────
# Returns 0 (success) if the monad status is "ok", non-zero otherwise.
# Arguments:
#   $1 — the Return JSON string
Return::is_ok() {
  local json="$1"
  local status
  status=$(jq -r '.status' <<< "$json" 2>/dev/null) || return 1
  [[ "$status" == "ok" ]]
}

# ── Return::data ──────────────────────────────────────────────────────────────
# Extracts the .data field from a success monad.
# Arguments:
#   $1 — the Return JSON string
Return::data() {
  local json="$1"
  jq -r '.data' <<< "$json" 2>/dev/null
}

# ── Return::message ───────────────────────────────────────────────────────────
# Extracts the .message field from a failure monad.
# Arguments:
#   $1 — the Return JSON string
Return::message() {
  local json="$1"
  jq -r '.message' <<< "$json" 2>/dev/null
}

# ── Return::code ──────────────────────────────────────────────────────────────
# Extracts the .code field from a failure monad (defaults to 1).
# Arguments:
#   $1 — the Return JSON string
Return::code() {
  local json="$1"
  jq -r '.code // 1' <<< "$json" 2>/dev/null
}

# ── Return::chain ─────────────────────────────────────────────────────────────
# Chains two Return monad-producing commands. If the first fails, propagates the
# failure without evaluating the second.
# Arguments:
#   $1 — first command (should output Return JSON)
#   $2 — second command (receives first's .data via stdin)
# Example:
#   result=$(Return::chain "$(fetch_user)" "jq '.name'")
Return::chain() {
  local first="$1"
  local second="$2"
  local first_result

  first_result=$(eval "$first" 2>/dev/null) || {
    Return::failure "Command failed: $first"
    return 1
  }

  if Return::is_ok "$first_result"; then
    local data
    data=$(Return::data <<< "$first_result")
    echo "$data" | eval "$second" 2>/dev/null || {
      Return::failure "Chain step failed: $second"
      return 1
    }
  else
    echo "$first_result"
  fi
}

# ── Return::map ──────────────────────────────────────────────────────────────
# Applies a transformation function to the .data field of a success monad.
# If the monad is a failure, passes it through unchanged.
# Arguments:
#   $1 — the Return JSON string
#   $2 — the transformation (a command that reads from stdin)
# Example:
#   result=$(Return::map "$(my_fn)" "jq '.name | upcase'")
Return::map() {
  local json="$1"
  local transform="$2"

  if Return::is_ok "$json"; then
    local data
    data=$(Return::data <<< "$json")
    local transformed
    transformed=$(echo "$data" | eval "$transform" 2>/dev/null) || transformed="null"
    Return::success "$transformed"
  else
    echo "$json"
  fi
}

# ── Private: _detect_type ─────────────────────────────────────────────────────
# Detects whether a value is a JSON primitive, string, or empty.
Return::_detect_type() {
  local value="$1"
  [[ -z "$value" ]] && echo "null" && return
  # Check if it's valid JSON (number, boolean, null, array, object)
  if jq -e "$value" &>/dev/null; then
    echo "json"
  else
    echo "string"
  fi
}

# ── Private: _escape_json_string ─────────────────────────────────────────────
# Escapes a string for safe embedding in JSON double-quotes.
Return::_escape_json_string() {
  local str="$1"
  # Escape backslashes, quotes, newlines, tabs, carriage returns, and form-feeds
  printf '%s' "$str" \
    | sed 's/\\/\\&/g' \
    | sed 's/"/\\"/g' \
    | sed ':a;N;$!ba;s/\n/\\n/g' \
    | sed 's/\t/\\t/g' \
    | sed 's/\r/\\r/g' \
    | sed 's/\f/\\f/g'
}

# ── Private: _json_quote ──────────────────────────────────────────────────────
# Quotes a string for safe eval assignment (used by Return::unwrap).
Return::_json_quote() {
  local val
  read -r val
  printf '%s' "$val" | sed 's/'\''/'\'\\\\\'\''/g' | sed "s/^/\'/;s/$/\'/"
}
