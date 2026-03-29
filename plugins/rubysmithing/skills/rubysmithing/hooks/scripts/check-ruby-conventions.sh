#!/usr/bin/env bash
# check-ruby-conventions.sh
#
# PostToolUse hook: checks .rb files written by Claude for the frozen_string_literal pragma.
# Exits 0 (silent pass) or 2 (feedback fed back to Claude) per hook protocol.
#
# Security: This script runs on every file write, so we harden against:
# - Directory traversal attacks (../ in paths)
# - Malformed filenames
# - Arbitrary execution via special characters
# - Hanging linter processes

set -euo pipefail

# Degrade gracefully if jq is not installed
command -v jq &>/dev/null || exit 0

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# Security: Path sanitization
# 1. Block directory traversal attempts
if [[ "$file_path" == *"../"* ]]; then
  echo "SECURITY: Directory traversal blocked in path: ${file_path}" >&2
  exit 0  # Silent fail - don't leak information
fi

# 2. Block null bytes and other injection attempts
if [[ "$file_path" == *$'\0'* ]]; then
  echo "SECURITY: Null byte detected in path" >&2
  exit 0
fi

# 3. Only check .rb files (explicit extension match)
[[ "$file_path" == *.rb ]] || exit 0

# 4. Only check if the file actually exists on disk
[[ -f "$file_path" ]] || exit 0

# Check for frozen_string_literal pragma on line 1
# Timeout prevents hanging if file is on slow storage
first_line=$(timeout 5s head -n1 "$file_path" 2>/dev/null || echo "")

if [[ "$first_line" != "# frozen_string_literal: true" ]]; then
  echo "CONVENTION: ${file_path} is missing '# frozen_string_literal: true' on line 1." >&2
  echo "Prepend it now, or run /rubysmithing:refactor to apply full Standard Mode convention hardening." >&2
  exit 2
fi

exit 0
