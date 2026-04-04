---
name: bashsmithing-context
description: CLI tool documentation verification sub-skill for Bash development. Automatically activates on mention of external CLI tools — like jq, fzf, gum, gh, shellcheck, bats, awk, sed, find, etc. — and verifies current flags and usage patterns before code generation. Uses codesearch, webfetch, and man pages to resolve syntax. Results are cached in ~/.bashsmithing/context_cache.json. If verification fails, injects an explicit [WARNING: Unverified CLI Syntax] block. Pairs with bash-script-generator and rubysmithing as a prerequisite step.
---

# Bashsmithing — Context

CLI Tool Documentation Resolver. Verifies external command syntax before generation.
Caches results to minimize lookups. Fails loudly — never silently.

## When This Skill Activates

Activate on first mention of any external CLI tool or when generating complex shell pipelines.
Priority tools for verification (flags change across versions/platforms):

- `jq` — JSON processing
- `fzf` — fuzzy finder
- `gum` — Charm terminal UI
- `gh` — GitHub CLI
- `shellcheck` — linter
- `bats` — testing framework
- `curl` — HTTP client
- `git` — version control
- `awk`, `sed`, `find` — POSIX vs GNU vs BSD variants

Skip lookup for: built-ins (`cd`, `echo`, `read`), tools already resolved this session.

## Step 1: Check Session Cache

Before any external search, check if the tool was resolved in this session's memory.
Track resolved tools as:

```json
{
  "jq": { "resolved": true, "source": "official_docs", "last_verified": "2026-03-19" },
  "fzf": { "resolved": true, "source": "man_page", "last_verified": "2026-03-19" }
}
```

If cached → use cached result directly, skip Steps 2–4.

## Step 2: Check Persistent JSON Cache

Check `~/.bashsmithing/context_cache.json`.
If the entry exists and is less than 30 days old, load it into the session cache and return.
If the entry is older than 30 days (stale), proceed to Step 3 but mark it as a potential fallback.

## Step 3: Resolve Tool Mapping

Look up the tool in `references/cli-registry.md`.
Determine the primary documentation source (URL, man page, or search query).

## Step 4: Fetch Documentation

Execute a combination of tools based on the registry:

1. **`codesearch`**: Find real-world usage patterns in GitHub or local codebase.
2. **`webfetch`**: Pull content from official documentation URLs.
3. **`bash` (man)**: Run `man [tool]` and capture the output (if available locally).

Extract:
- Correct flag syntax (especially for platform-dependent flags).
- Required arguments.
- Example usage patterns.
- Common pitfalls or version-specific behavior.

## Step 5: Cache and Return

Update the persistent JSON cache at `~/.bashsmithing/context_cache.json`.
Return to the requesting skill:
- Tool name + Source used.
- Relevant flag syntax and descriptions.
- Minimal working example.
- Any platform-specific warnings (e.g., macOS/BSD vs Linux/GNU).

## Failure Protocol

If resolution fails (timeout, no results, empty docs):

**Do not silently fall back to training data.**

Inject this block at the top of the generated bash script (or above the usage block):

```bash
# [WARNING: Unverified CLI Syntax]
# Documentation could not be resolved for: [tool_name]
# This code is based on training data and MAY be outdated or incorrect.
# Verify against: [official_docs_url_from_registry]
# Run: man [tool_name] or [tool_name] --help to check flags.
```

Then proceed with best-effort generation, flagging every usage of the unverified tool with an inline `# unverified` comment.

## Persistence Schema

The cache at `~/.bashsmithing/context_cache.json` follows this format:

```json
{
  "tools": {
    "jq": {
      "url": "https://jqlang.github.io/jq/manual/",
      "flags": ["-r", "-c", "--arg", "--slurp"],
      "examples": ["jq -r '.key' file.json"],
      "resolved_at": "2026-03-19T10:00:00Z",
      "ttl_days": 30
    }
  }
}
```

## Related Skills

- **bash-script-generator**: Use for the final script output.
- **rubysmithing**: When CLI tools are used within Ruby orchestration.
- **shellcheck**: To verify the generated syntax is actually valid.
