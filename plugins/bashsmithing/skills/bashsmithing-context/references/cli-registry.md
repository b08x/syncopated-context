# CLI Tool Registry

Mapping of common CLI tools to their documentation sources, usage search patterns, and common pitfalls.

## Core Registry

| Tool | Official Docs URL | Codesearch Query | Key Flags |
| :--- | :--- | :--- | :--- |
| `jq` | https://jqlang.github.io/jq/manual/ | `(?s)jq.*'\.'` | `-r` (raw), `-c` (compact), `--arg` |
| `fzf` | https://github.com/junegunn/fzf#usage | `fzf --filter` | `--multi`, `--preview`, `--query` |
| `gum` | https://github.com/charmbracelet/gum | `gum choose` | `choose`, `input`, `spin`, `confirm` |
| `gh` | https://cli.github.com/manual/ | `gh pr create` | `api`, `issue`, `pr`, `repo`, `auth` |
| `shellcheck` | https://www.shellcheck.net/wiki/ | `shellcheck -f json` | `-s` (shell), `-e` (exclude) |
| `bats` | https://bats-core.readthedocs.io/ | `(?s)@test.*run` | `load`, `run`, `assert` |
| `curl` | https://curl.se/docs/manpage.html | `curl -sSL` | `-f` (fail), `-o` (output), `-H` (header) |
| `git` | https://git-scm.com/doc | `git -C` | `-C` (path), `rev-parse`, `log --format` |

## Detailed Tool Analysis

### jq
- **Common Pitfalls:** Single quotes for filter, unquoted variable injection.
- **Best Practice:** Use `--arg` to pass shell variables to `jq` safely.
- **Usage:** `jq -r '.key' file.json`

### fzf
- **Common Pitfalls:** Assuming `fzf` is in PATH in non-interactive shells.
- **Best Practice:** Check `command -v fzf` and provide fallback.
- **Usage:** `selected=$(find . -type f | fzf)`

### gum
- **Common Pitfalls:** Hanging in non-interactive/CI environments.
- **Best Practice:** Use `GUM_OPTS="--non-interactive"` or similar guards.
- **Usage:** `gum confirm "Deploy?" && deploy_script`

### gh (GitHub CLI)
- **Common Pitfalls:** Missing `GITHUB_TOKEN` in scripts, rate limits.
- **Best Practice:** Use `gh api` for complex queries, handle non-zero exits.
- **Usage:** `gh pr list --state open --json number,title`

### shellcheck
- **Common Pitfalls:** Ignoring SC2086 (unquoted variables).
- **Best Practice:** Run as part of CI, use directives for intentional ignores.
- **Usage:** `shellcheck script.sh`

### bats (Bash Automated Testing System)
- **Common Pitfalls:** Using `source` instead of `load` for helper libs.
- **Best Practice:** Use `bats-assert` and `bats-support` libraries.
- **Usage:** `@test "sanity" { run true; [ "$status" -eq 0 ]; }`

### curl
- **Common Pitfalls:** Silent failure on 4xx/5xx errors without `-f`.
- **Best Practice:** Always use `-fSL` for robust downloads.
- **Usage:** `curl -fSL -o output.tar.gz https://example.com/file`

### git
- **Common Pitfalls:** Hardcoded paths, assuming main/master branch name.
- **Best Practice:** Use `git rev-parse --show-toplevel` and `git symbolic-ref`.
- **Usage:** `git rev-parse HEAD`
