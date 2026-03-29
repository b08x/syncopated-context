# Cache CLI Reference

Human-readable (`pp`) output by default; add `--json` for machine-readable output.

```bash
# Fresh fetch — respects TTL (7 days); returns miss if absent or expired
ruby scripts/context_cache.rb fetch <gem> [--json]

# Alias for fetch (backward compat)
ruby scripts/context_cache.rb check <gem> [--json]

# Stale fetch — ignores TTL; returns any entry regardless of age
ruby scripts/context_cache.rb stale <gem> [--json]

# Upsert resolved entry; sigs_json is a JSON array string, example is a single-quoted string
ruby scripts/context_cache.rb store <gem> <context7_id> [sigs_json] [example]

# List all cached gems with age and staleness status
ruby scripts/context_cache.rb list [--json]

# Remove entry to force fresh lookup on next use
ruby scripts/context_cache.rb evict <gem>
```

**Exit codes:**

| Command       | Exit 0          | Exit 1       | Exit 2              |
|---------------|-----------------|--------------|---------------------|
| fetch / check | entry found     | miss / error | —                   |
| stale         | found + fresh   | miss         | found but stale     |
| store         | stored ok       | parse error  | —                   |
| list / evict  | always 0        | —            | —                   |

**`--json` output shapes (fetch/check hit):**

```json
{"status":"fresh","gem_name":"ruby_llm","context7_id":"/crmne/ruby_llm",
 "method_sigs":[".chat(...)"],"example":"...","resolved_at":"2026-03-11",
 "age_days":7.0,"ttl_days":7}
```

Miss: `{"status":"miss"}`

**stale hit (exit 2):** same shape + `"status":"stale"` + `"warning":"<pre-formatted block>"`

**store:** `{"status":"stored","gem_name":"ruby_llm"}` (or `Stored: ruby_llm` without `--json`)

**list `--json`:** JSON array of entry objects with string keys.
