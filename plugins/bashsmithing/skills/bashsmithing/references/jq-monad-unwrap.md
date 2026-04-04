# jq Monad Unwrap Guide

Guide for AI agents on how to safely unwrap `Return::success` and `Return::failure`
JSON monads using `jq`. All bashsmithing scripts should use these patterns instead of
bare `echo` or `return`.

---

## Return Monad Shapes

Every `Return::*` function emits a single JSON object to stdout. Never to stderr.

### Success
```bash
Return::success "data"
# {"status":"ok","data":"data"}

Return::success ""          # empty data
# {"status":"ok","data":null}

Return::success '{"key":"value"}'  # already JSON — passed through
# {"status":"ok","data":{"key":"value"}}

Return::success "42"
# {"status":"ok","data":42}
```

### Failure
```bash
Return::failure "file not found" 1
# {"status":"error","message":"file not found","code":1}

Return::failure "permission denied"
# {"status":"error","message":"permission denied","code":1}
```

---

## The Safe Unwrap Pattern

Always capture the full output first, then inspect it. Never pipe directly.

```bash
result=$(my_function)
# ^^^ Capture BEFORE any jq — piping loses exit code context
```

### Check status with jq -e

The `-e` flag makes jq exit 2 on null/missing values, which is perfect for status checks:

```bash
result=$(my_function)

# If ok, extract data
if jq -e '.status == "ok"' <<< "$result" &>/dev/null; then
  data=$(jq -r '.data' <<< "$result")
  echo "Got: $data"
else
  msg=$(jq -r '.message' <<< "$result")
  echo "Error: $msg" >&2
fi
```

### One-liner extraction

```bash
# Extract data (returns empty string on error)
data=$(jq -r 'if .status == "ok" then .data else empty end' <<< "$result")

# Extract error message (returns empty string on success)
msg=$(jq -r 'if .status == "error" then .message else empty end' <<< "$result")

# Extract error code (returns 1 if missing)
code=$(jq -r 'if .status == "error" then .code else 1 end' <<< "$result")
```

---

## jq Filter Reference

### Status check
```bash
jq -e '.status == "ok"' <<< "$result"    # exit 0 if ok, exit 1 if error
jq -e '.status == "error"' <<< "$result" # exit 0 if error, exit 1 if ok
```

### Data extraction
```bash
jq -r '.data'           <<< "$result"  # raw string output
jq -e '.data'           <<< "$result"  # with exit 2 on null
jq -r '.data // "fallback"' <<< "$result"  # with fallback
```

### Nested data (when Return::success was passed JSON)
```bash
# When data is a JSON object
jq -r '.data.name' <<< "$result"        # extract nested field
jq -r '.data[] | .id' <<< "$result"    # iterate array in data

# Validate and extract
jq -r '.data | select(.active == true) | .id' <<< "$result"
```

### Error extraction
```bash
jq -r '.message' <<< "$result"          # error message
jq -r '.code // 1'  <<< "$result"      # error code (default 1)
jq -r '.code == 2'  <<< "$result"     # specific error code check
```

---

## Helper Functions from lib/monad.sh

These are always available after sourcing `lib/monad.sh`:

### Return::unwrap — two variables at once
```bash
Return::unwrap "$(my_function)" "value" "ok"
if [[ "$ok" == "0" ]]; then
  echo "Success: $value"
else
  echo "Failed: $value"
fi
```

### Return::is_ok — boolean check
```bash
result=$(my_function)
if Return::is_ok "$result"; then
  data=$(Return::data "$result")
fi
```

### Return::data / Return::message — shorthand extractors
```bash
data=$(Return::data "$result")    # exits 1 if not ok
msg=$(Return::message "$result")   # exits 1 if status was ok
```

### Return::chain — pipe two monads
```bash
# Fetch user, then extract name — stops if first fails
result=$(Return::chain "$(fetch_user)" "jq '.name'")
```

### Return::map — transform data in-place
```bash
# Uppercase the data field
result=$(Return::map "$(my_fn)" "jq -r '.data | ascii_upcase'")
```

---

## Common Patterns

### Pattern: Guard with monad
```bash
validate_input() {
  local input="$1"
  [[ -z "$input" ]] && Return::failure "input is required"
  [[ ! -f "$input" ]] && Return::failure "file not found: $input"
  Return::success "$input"
}
```

### Pattern: Transform then unwrap
```bash
result=$(validate_input "$path")
if Return::is_ok "$result"; then
  data=$(Return::data "$result" | jq -r '. + "_processed"')
  echo "$data"
fi
```

### Pattern: Chained pipeline
```bash
result=$(
  Return::chain \
    "$(fetch_config)" \
    "jq '.database.url'" | \
    Return::chain \
    "$(connect_db)" \
    "jq '.connection_id'"
)
```

### Pattern: Batch processing
```bash
for file in "${files[@]}"; do
  result=$(process_file "$file")
  if Return::is_ok "$result"; then
    count=$(Return::data "$result")
    successes=$((successes + count))
  else
    msg=$(Return::message "$result")
    echo "Skipped $file: $msg" >&2
  fi
done
```

---

## Edge Cases

### Empty data field
```bash
Return::success ""  # emits data:null

# Safe extraction:
data=$(jq -r '.data // null' <<< "$result")
[[ "$data" != "null" ]] && echo "Got: $data"
```

### Data containing quotes
```bash
Return::success 'He said "hello"'

# Safe extraction — -r keeps raw strings:
data=$(jq -r '.data' <<< "$result")
echo "$data"  # He said "hello"
```

### Data containing newlines
```bash
Return::success $'line one\nline two'

# Safe extraction:
jq -r '.data' <<< "$result" | while IFS= read -r line; do
  echo "LINE: $line"
done
```

### Nested JSON in data
```bash
Return::success '{"name":"Alice","age":30}'

# Extract specific field from nested data:
name=$(jq -r '.data.name' <<< "$result")
age=$(jq -r '.data.age' <<< "$result")
```

### jq not available — degraded fallback
```bash
# If jq is missing, fall back to grep + sed (limited but safe):
if ! command -v jq &>/dev/null; then
  data=$(grep '"data"' <<< "$result" | sed 's/.*"data":"\?\([^"]*\)"\?.*/\1/')
else
  data=$(jq -r '.data' <<< "$result")
fi
```

---

## Common Mistakes

### ❌ Piping directly — loses the json
```bash
# WRONG — result is empty or wrong
data=$(my_function | jq -r '.data')
```

### ✅ Capture first, then extract
```bash
# RIGHT
result=$(my_function)
data=$(jq -r '.data' <<< "$result")
```

### ❌ Bare grep for status — fragile
```bash
# WRONG — fails on unusual data
if grep -q '"ok"' <<< "$result"; then ...
```

### ✅ jq -e for status — correct JSON parsing
```bash
# RIGHT
if jq -e '.status == "ok"' <<< "$result" &>/dev/null; then ...
```

### ❌ Using return to pass data
```bash
# WRONG — Bash return is exit code only, can't carry data
my_fn() { return "$(my_data)"; }  # BROKEN
```

### ✅ Using stdout for data, exit code for status
```bash
# RIGHT — stdout carries data, exit code carries control flow
my_fn() {
  [[ -f "$1" ]] && Return::success "$(cat "$1")" || Return::failure "not found"
}
```
