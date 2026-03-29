---
name: analyse
description: "Ruby-targeted analysis skill implementing Gemba Walk (code archaeology, docs-vs-reality gaps), Muda waste analysis (dead methods, N+1 queries, unused gems, over-engineering), Root-Cause Tracing (backward call-chain from symptom to source), and Five Whys (iterative causal drilling). Use when user asks \"why is this failing\", \"trace this bug\", \"root cause\", \"what's wasting cycles\", \"dead code audit\", \"gemba\", \"muda\", \"pre-refactor investigation\", or reports a Zeitwerk error, circuit_breaker trip, or slow query. Auto-selects method from context. Produces findings keyed to refactor pattern names for direct handoff."
---

# Rubysmithing — Analyse

Ruby-targeted diagnostic analysis. Identifies *why* problems exist and *where*
they originate — the step before `/rubysmithing:refactor` fixes them and
`/rubysmithing:report` verifies the result.

## Architecture

```
analyse/SKILL.md
  references/analyse-methods.md  — Full method templates, Ruby instrumentation
                                   idioms, Muda category mappings, Gemba
                                   observation checklist, defense-in-depth pattern
```

Load `references/analyse-methods.md` immediately when executing any method.

## Method Auto-Selection

Select the method from context signals. Accept explicit flags to override.

| Signal | Method |
|:-------|:-------|
| Error/exception, stack trace provided, "why is this failing", "why does X error" | Root-Cause Tracing |
| "what's slow", "bloated", "wasting", "dead code", "unused", "over-engineered" | Muda Analysis |
| "how does this work", "what does this actually do", "pre-refactor", unfamiliar area | Gemba Walk |
| "why", "why did this happen", recurring issue with no obvious cause | Five Whys |
| `--trace` flag | Root-Cause Tracing (explicit) |
| `--muda` flag | Muda Analysis (explicit) |
| `--gemba` flag | Gemba Walk (explicit) |
| `--why` flag | Five Whys (explicit) |

When the signal is ambiguous, default to Gemba Walk and state the assumption.

## Target Detection

- File path (`.rb`, `.gemspec`, `Gemfile`) → analyse that file
- Directory path → analyse the project as a whole
- No argument → analyse Ruby files in the current working directory
- Inline pasted code → analyse the provided snippet
- Stack trace pasted without a path → Root-Cause Tracing on the trace + context

## Method: Gemba Walk (Ruby Adaptation)

"Go see the actual code." Gemba Walk bridges the gap between assumed and actual
behavior — critical before refactoring anything unfamiliar.

**Process:**

1. **Define scope** — which file(s) or subsystem to observe
2. **State assumptions** — what the code is documented or expected to do
3. **Observe reality** — read actual code: entry points, data flow, require/autoload chain, Zeitwerk loader config vs. file structure
4. **Document surprises** — undocumented behavior, hidden dependencies, stale comments, dead branches, `puts`/`p` debug lines left in
5. **Identify gaps** — documentation vs. reality mismatches, missing `frozen_string_literal`, scattered config that should be `tty-config`
6. **Recommend** — update docs, route to refactor, or accept as intentional

Full observation checklist in `references/analyse-methods.md` — Gemba section.

## Method: Muda Waste Analysis (Ruby Adaptation)

Map the 7 waste types to Ruby code artifacts. Prioritize by impact.

| Waste Type | Ruby Code Manifestation |
|:-----------|:------------------------|
| Overproduction | Dead methods, unused public API, speculative abstractions, unused initializer args |
| Waiting | Synchronous calls that should use `Async { }`, missing `circuit_breaker` wrapping |
| Transportation | Redundant object transformations, repeated serialization/deserialization layers |
| Over-processing | Duplicated `dry-schema` contracts, excessive validation, over-instrumented logging |
| Inventory | Commented-out code, stale feature flags, unused Gemfile dependencies |
| Motion | Missing Zeitwerk compliance forcing manual `require`, config scattered across files |
| Defects | RuboCop violations, missing `frozen_string_literal`, silent `rescue` clauses |

Output: waste type → instances found (file:line) → estimated impact → refactor-patterns.md key.

Full category mappings with examples in `references/analyse-methods.md` — Muda section.

## Method: Root-Cause Tracing (Ruby Adaptation)

Trace bugs backward through the call chain to find the original trigger.
Never fix where the error appears — find where the bad value originated.

**Process:**

1. **Observe symptom** — error message, class, file:line
2. **Find immediate cause** — what code directly raises/produces this?
3. **Trace upward** — what called that? What value was passed?
4. **Keep tracing** — continue until reaching the original trigger (user input, config load, initializer, test setup)
5. **Find original trigger** — where did the bad value or bad state originate?
6. **Defense-in-depth** — after fixing at source, add guards at each layer up the chain

**Ruby instrumentation idioms** (use `$stderr` — not logger, which may be suppressed in tests):

```ruby
$stderr.puts caller.join("\n")                    # full call chain
$stderr.puts method(:foo).source_location.inspect # where method is defined
$stderr.puts self.class                           # unexpected receiver type
```

**Common Ruby trace patterns:**
- `NameError: uninitialized constant Foo` → which file was expected → Zeitwerk loader config → inflector → actual file path on disk
- `circuit_breaker opens` → which external call → what error → configured threshold → configuration source (env var, tty-config, hardcoded)
- `Sequel::Error` deep in pipeline → N+1 origin → model association → eager loading omission
- `dry-schema contract violation` → which field → upstream transformer → input boundary

Full tracing template and defense-in-depth pattern in `references/analyse-methods.md` — Root-Cause section.

## Method: Five Whys (Ruby Adaptation)

Iteratively ask "why" to move from surface symptom to systemic root cause.
Particularly useful for recurring issues (same error type across multiple files/sessions).

**Process:**

1. **State problem clearly** — precise symptom with context
2. **Ask "Why?" → document answer**
3. **For that answer, ask "Why?" again**
4. **Continue ~5 iterations** until the answer is a systemic or process cause
5. **Validate backward** — root cause should produce the symptom when you reason forward
6. **Explore branches** — when multiple causes exist, trace each separately

**Ruby-specific stopping points** (systemic causes worth stopping at):
- Convention detection missing from Gemfile or `.rubocop.yml` (process gap)
- Zeitwerk loader configured with incorrect root or inflector (configuration source)
- `circuit_breaker` policy absent in a class that makes external calls (architectural gap)
- Test suite using stubs/mocks that diverge from real gem behavior (test design issue)

## Output Format

```
METHOD: [Gemba Walk | Muda Analysis | Root-Cause Tracing | Five Whys]
TARGET: [file path | directory | snippet]
CONVENTION TARGET: [RuboCop | StandardRB | Rubysmith | community idioms]

[Method findings — structured per method above]

ACTIONABLE NEXT STEPS:
- [Finding] → /rubysmithing:refactor [file] (pattern: [refactor-pattern-key])
- [Finding] → /rubysmithing:sift --advisory for full QA assessment
- [Finding] → manual intervention required ([describe why])
```

For Root-Cause Tracing, include the trace chain explicitly:
```
SYMPTOM → IMMEDIATE CAUSE → [intermediate steps] → ORIGINAL TRIGGER
Fix at: [source location]
Defense layers: [file:line guard 1] / [file:line guard 2] / [boundary validation]
```

## Integration with refactor

Findings reference named patterns from
`$CLAUDE_PLUGIN_ROOT/skills/refactor/references/refactor-patterns.md` wherever a match exists.
This enables direct handoff: the refactor agent receives a pre-keyed issue list
rather than freeform descriptions.

## Integration with sift

When analysis reveals issues beyond the current target scope (architectural
drift, systematic convention gaps, missing DI boundaries), suggest
`/rubysmithing:report` for a full SIFT assessment. Analysis and report are
complementary: analyse answers *why*, SIFT answers *how bad* and *what next*.
