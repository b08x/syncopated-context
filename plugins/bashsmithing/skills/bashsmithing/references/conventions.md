# Bashsmithing Conventions

Strict conventions for production-grade Bash 3.2+ scripts. These rules ensure
portability, safety, and maintainability.

## Shell Execution & Strict Mode

Every script must start with a proper shebang and strict mode configuration.

```bash
#!/usr/bin/env bash
# shellcheck shell=bash

set -euo pipefail
IFS=$'\n\t'
```

- `set -e`: Exit immediately if a command fails
- `set -u`: Treat unset variables as an error
- `set -o pipefail`: Ensure pipeline exit status reflects the last non-zero exit
- `IFS=$'\n\t'`: Prevent word splitting on spaces

## Namespacing & Functions

Use a namespacing pattern to avoid collisions and emulate object-oriented modularity.

### Namespace Pattern
Functions should be named with a double-colon prefix if part of a library.
`Namespace::function_name()`

### Function Standards
- Use `snake_case` for all function names.
- Always use the `function` keyword or `name()` syntax consistently (prefer `name()`).
- Use the `local` keyword for **all** variables inside functions.
- No global variables should be declared outside functions unless they are configuration constants.

```bash
Bashsmith::monad_success() {
  local value="${1:-}"
  printf "SUCCESS: %s\n" "$value"
}
```

## Internal State & Scope

- **NO globals**: Use functions to encapsulate logic.
- **local everything**: Every variable in a function must be `local`.
- **readonly constants**: Use `readonly` for configuration values that shouldn't change.

## Error Handling: Monads

Standard mode requires the use of Return monads from `lib/monad.sh`.

- `Return::success "message"`: Signals a successful operation.
- `Return::failure "error code" "message"`: Signals a failure with context.

Functions should use guard clauses to return early on error.

```bash
MyModule::process_data() {
  local input="${1:-}"

  [[ -z "$input" ]] && {
    Return::failure "MISSING_INPUT" "input is required"
    return 1
  }

  # ... implementation
  Return::success "Processed $input"
}
```

## Safe Command Execution

- **Quotes**: Always double-quote variable expansions: `"$var"`.
- **Parameter Expansion**: Use defaults where appropriate: `"${var:-default}"`.
- **Subshells**: Wrap risky or environment-altering commands in subshells `( )` to
  prevent leaking side effects (like `cd`).
- **Guard Clauses**: Check for dependencies or preconditions at the start of
  functions.

## Logging & Output

- Use the `logger` builtin for system-level logging.
- Use structured `echo` or `printf` for console output, following a consistent
  format (e.g., `[INFO]`, `[ERROR]`).

## Shellcheck Compliance

- All code must be Shellcheck-clean.
- Include `shellcheck` directives for intentional overrides.
- Reference the project's `.shellcheckrc`.
