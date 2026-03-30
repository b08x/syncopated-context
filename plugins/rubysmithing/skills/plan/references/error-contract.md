# Rubysmithing Error Contract

All rubysmithing sub-agents MUST use this schema when propagating unresolvable errors to the orchestrator. Structured errors allow the orchestrator to make intelligent recovery decisions rather than receiving opaque failure messages.

## ErrorContext Schema

```ruby
# Conceptual schema — embed as a YAML block or structured prose in your error response
ErrorContext:
  errorCategory:   # "transient" | "validation" | "business" | "permission"
  isRetryable:     # true | false
  failedStep:      # Which step failed (e.g., "Context7 resolution", "Cache fetch", "Gem API parse")
  attemptedQuery:  # The exact query/command that failed
  partialResults:  # Any partial output produced before failure (omit if none)
  alternativeSuggestion: # Optional: what the orchestrator could try instead
  coverageGaps:    # List of topics/gems/files not covered due to failure
```

## Error Categories

| Category | Meaning | isRetryable |
|:---------|:--------|:-----------:|
| `transient` | Network timeout, rate limit, MCP unavailable | `true` |
| `validation` | Bad input, unresolvable gem name, malformed file | `false` |
| `business` | Gem not in registry, no conventions file, scope mismatch | `false` |
| `permission` | File unreadable, write blocked by hook | `false` |

## Wire Format

When propagating an error, prepend a `[AGENT ERROR]` block before any partial output:

```
[AGENT ERROR]
errorCategory: transient
isRetryable: true
failedStep: Context7 resolution
attemptedQuery: resolve-library-id "some_gem"
partialResults: none
alternativeSuggestion: retry with pre-mapped ID from gem-registry.md
coverageGaps: ["some_gem API signatures"]
[/AGENT ERROR]
```

## What NOT to Do

- Do NOT return a bare "operation failed" string — the orchestrator cannot recover from that
- Do NOT silently suppress errors and return empty results as if successful
- Do NOT use generic "unavailable" status that hides whether the failure is retryable
- Do NOT omit `coverageGaps` — the orchestrator uses this to annotate final output with missing coverage

## Orchestrator Response to Structured Errors

When the orchestrator receives a `[AGENT ERROR]` block:

1. `isRetryable: true` → attempt one re-delegation using `alternativeSuggestion` if present
2. `isRetryable: false` → annotate the final output with `coverageGaps`, continue workflow without the failed component
3. Multiple errors from parallel sub-agents → merge all `coverageGaps` into a single coverage gap annotation in final output

## Anti-Pattern: Silent Success

```
# BAD — orchestrator cannot detect failure
return "No documentation found."

# GOOD — orchestrator can recover intelligently
[AGENT ERROR]
errorCategory: transient
isRetryable: true
failedStep: Context7 query
attemptedQuery: query-docs "ruby_llm chat streaming"
partialResults: none
alternativeSuggestion: check stale SQLite cache
coverageGaps: ["ruby_llm streaming API"]
[/AGENT ERROR]
```
