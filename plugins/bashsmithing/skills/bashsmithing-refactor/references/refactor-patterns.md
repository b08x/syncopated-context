# Bash Refactor Patterns

Named patterns for bashsmithing-refactor. Each entry maps an anti-pattern key to a before/after transformation.

---

## global_variables
**Severity:** CRITICAL
**Area:** architecture
**Trigger:** VAR=value outside functions

```bash
# Before
USER_ID=1000
DATA_DIR="/tmp/data"

process_data() {
  echo "Processing $DATA_DIR for $USER_ID"
}

# After
readonly DATA_DIR="/tmp/data"

process_data() {
  local user_id="${1:-1000}"
  echo "Processing $DATA_DIR for $user_id"
}
```

---

## missing_pipefail
**Severity:** CRITICAL
**Area:** safety
**Trigger:** Missing `set -o pipefail`

```bash
# Before
#!/usr/bin/env bash
grep "error" log.txt | awk '{print $2}'

# After
#!/usr/bin/env bash
set -o pipefail
grep "error" log.txt | awk '{print $2}'
```

---

## missing_errexit
**Severity:** CRITICAL
**Area:** safety
**Trigger:** Missing `set -o errexit` or `set -e`

```bash
# Before
#!/usr/bin/env bash
cd /nonexistent_dir
rm -rf * # Disaster!

# After
#!/usr/bin/env bash
set -o errexit
cd /nonexistent_dir
rm -rf * # Script exits before rm runs
```

---

## unquoted_variables
**Severity:** ERROR
**Area:** style
**Trigger:** Shellcheck SC2086

```bash
# Before
rm $filename
if [ $name == "admin" ]; then

# After
rm "$filename"
if [[ "$name" == "admin" ]]; then
```

---

## unchecked_command_substitution
**Severity:** ERROR
**Area:** safety
**Trigger:** $(cmd) without error handling

```bash
# Before
output=$(complex_command)
echo "$output"

# After
if ! output=$(complex_command); then
  echo "Error: complex_command failed" >&2
  exit 1
fi
echo "$output"
```

---

## echo_over_logger
**Severity:** ERROR
**Area:** logging
**Trigger:** Using `echo` for system logs

```bash
# Before
echo "Task started at $(date)"
echo "Error: database connection failed"

# After
# Assuming a standard logger function is defined
log_info "Task started"
log_error "Database connection failed"
```

---

## flat_script
**Severity:** ERROR
**Area:** architecture
**Trigger:** Logic entirely in global scope

```bash
# Before
# 100 lines of logic directly in the file

# After
main() {
  parse_args "$@"
  validate_env
  run_logic
}

main "$@"
```

---

## hardcoded_paths
**Severity:** WARNING
**Area:** portability
**Trigger:** Absolute paths like `/usr/local/bin/`

```bash
# Before
/usr/local/bin/aws s3 ls

# After
readonly AWS_BIN=$(command -v aws)
"$AWS_BIN" s3 ls
```

---

## silent_fail
**Severity:** ERROR
**Area:** safety
**Trigger:** Command failure ignored

```bash
# Before
cp source destination
mv destination final

# After
cp source destination || { echo "Failed to copy"; exit 1; }
mv destination final   || return 1
```

---

## glob_without_check
**Severity:** WARNING
**Area:** safety
**Trigger:** `rm *.txt` without verifying matches

```bash
# Before
rm *.txt

# After
for f in *.txt; do
  [[ -f "$f" ]] || continue
  rm "$f"
done
```

---

## unused_variables
**Severity:** INFO
**Area:** style
**Trigger:** Shellcheck SC2034

```bash
# Before
foo="unused"
echo "bar"

# After
echo "bar"
```

---

## function_name_case
**Severity:** WARNING
**Area:** style
**Trigger:** CamelCase or PascalCase functions

```bash
# Before
function ProcessData() { :; }

# After
process_data() { :; }
```

---

## missing_local
**Severity:** ERROR
**Area:** safety
**Trigger:** Loop variables in functions leaking to global scope

```bash
# Before
update_all() {
  for i in {1..5}; do
    echo "$i"
  done
}

# After
update_all() {
  local i
  for i in {1..5}; do
    echo "$i"
  done
}
```

---

## word_split
**Severity:** ERROR
**Area:** safety
**Trigger:** `for x in $(cmd)`

```bash
# Before
for file in $(ls *.txt); do
  cat $file
done

# After
while IFS= read -r file; do
  cat "$file"
done < <(find . -maxdepth 1 -name "*.txt" -print)
```

---

## sc2086
**Severity:** ERROR
**Area:** style
**Trigger:** Double quote to prevent globbing and word splitting

```bash
# Before
ls $directory

# After
ls "$directory"
```
