---
description: Check or warm the rubysmithing gem API cache. Resolves current method signatures via Context7 MCP and persists results to the SQLite cache.
argument-hint: "<gem-name>"
allowed-tools: ["Bash", "Read"]
---

Check the rubysmithing gem API cache for the gem provided in the arguments.

**If a gem name was provided:**

1. Run the cache check:
   ```bash
   ruby $CLAUDE_PLUGIN_ROOT/scripts/context_cache.rb check <gem-name> --json
   ```
2. If `"status": "fresh"` — display: gem name, Context7 ID, age in days, key method signatures, minimal example.
3. If `"status": "miss"` — resolve and cache:
   - Use `mcp__plugin_context7_context7__resolve-library-id` with the gem name
   - Check `$CLAUDE_PLUGIN_ROOT/references/gem-registry.md` for pre-mapped IDs first
   - Use `mcp__plugin_context7_context7__query-docs` with a targeted query: `"[gem] key usage patterns"`
   - Store the result:
     ```bash
     ruby $CLAUDE_PLUGIN_ROOT/scripts/context_cache.rb store <gem> <context7_id> '[sigs_json]' 'example'
     ```
   - Display the resolved signatures and example.
4. If `"status": "stale"` — display the cached result with a staleness warning and the `warning` field content.

**If no gem name was provided:**

List all cached entries:
```bash
ruby $CLAUDE_PLUGIN_ROOT/scripts/context_cache.rb list
```

Display the gem list as a table: gem name | Context7 ID | age | status (fresh/stale).

Always clearly report the cache status for each gem shown.
