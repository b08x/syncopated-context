---
name: context
description: Gem API verification sub-skill for Ruby development. Manages context boundaries by resolving current method signatures and usage examples via Context7 MCP. References a master gems inventory (CSV) for library IDs and formulates context-aware queries to ensure relevant documentation retrieval. Results are cached across sessions in SQLite. Pairs with plan, genai, and tui as a prerequisite step.
---

# Rubysmithing — Context

Context7-powered gem API resolver and context boundary manager.
Resolves method signatures and usage patterns before generating code.

## When This Skill Activates

Activate on first mention of any gem not in Ruby stdlib.
Skip lookup for: stdlib, gems already resolved this session, Lite Mode tasks.

## Step 1: Check Persistent Cache

Before calling Context7, check the SQLite persistent cache:

```bash
result=$(ruby $CLAUDE_PLUGIN_ROOT/scripts/context_cache.rb fetch GEMNAME --json)
# {"status":"fresh",...} → use cached result directly, skip Steps 2–4
```

## Step 2: Resolve Library ID from Master List

Consult the master list at `$CLAUDE_PLUGIN_ROOT/references/gems-inventory.csv`.

1.  **Search the CSV**: Look up the `gem` name and retrieve the `context7_id` (6th column).
2.  **Fallback**: If not in CSV, check `$CLAUDE_PLUGIN_ROOT/references/gem-registry.md`.
3.  **Resolve**: If still not found, use `Context7:resolve-library-id`.

## Step 3: Formulate Context-Aware Query

Use `Context7:query-docs` with a targeted query formulated from the current task context.

**Query Construction Pattern:**
`"[gem] [functional-task] [integration-context]"`

Examples:
- `"ruby_llm tools dry-schema validation"` (when using LLM with schema validation)
- `"sequel pgvector vector similarity search"` (when doing vector search)
- `"bubbletea update view lifecycle"` (when building a TUI)

## Step 4: Extract and Verify

Extract method signatures, parameter names, and a minimal working example.
Identify any deprecation warnings or breaking changes noted in the documentation.

## Step 5: Cache and Return

Store results in the persistent cache:

```bash
ruby $CLAUDE_PLUGIN_ROOT/scripts/context_cache.rb store GEMNAME CONTEXT7_ID \
  '[".method_one(arg:)", ".method_two"]' \
  'GemClass.new.call'
```

Return to the requesting skill:
- Verified method signatures
- Minimal working example
- Any warnings (deprecation, unverified state)

---

## Context Boundary Management

You define the "slice" of relevant documentation.
1.  **Scope**: Do not just fetch the gem's landing page; fetch the documentation for the specific methods needed for the task.
2.  **Integration**: If multiple gems are being used (e.g., `dspy.rb` + `ruby_llm`), ensure the query covers how they interact.
3.  **Freshness**: Prefer the master list and Context7 over training data to ensure current API compliance.

## Degradation Protocol

If Context7 is unreachable:
1.  **Tier 1**: Use stale cache from SQLite.
2.  **Tier 2**: Use descriptions from `gems-inventory.csv` to infer behavior.
3.  **Tier 3**: Inject `[WARNING: Unverified API Syntax]` and flag calls with `# unverified`.
