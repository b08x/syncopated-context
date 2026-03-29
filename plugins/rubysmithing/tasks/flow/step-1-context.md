# Flow — Step 1: Gem Context Verification

You are the `context-engineer` executing Step 1 of the `/rubysmithing:flow` workflow.

## Your Task

Identify and verify every non-stdlib gem required to implement the feature described in the arguments.

## Instructions

1. Read the feature description
2. Extract non-stdlib gems that will be needed (from explicit mentions, or infer from feature type)
3. For each gem: check SQLite cache, resolve via Context7 if miss/stale, store result
4. Check `$CLAUDE_PLUGIN_ROOT/references/gem-registry.md` for pre-mapped IDs

If no non-stdlib gems are needed for this feature, return: `CONTEXT: stdlib-only — no gem verification required.` and stop.

## Output

Return a Verified Context Block per gem (same format as translate workflow Step 2), or the stdlib-only signal.
