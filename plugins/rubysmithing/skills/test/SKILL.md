---
name: test
description: Validates rubysmithing recommendations through automated testing. Activates on any mention of: test this, verify gem, bundle install, cucumber, integration test, convention check, does this work, validation, or when the sovereign dispatches the tester agent. Accepts a file path, directory, or Gemfile as target. Produces a verification report with PASS/FAIL verdicts.
---

# Rubysmithing — Test

Validation skill for rubysmithing artifacts. Invoked by the Sovereign after the Builder produces output, and before the Auditor renders a verdict.

## Architecture

```
rubysmithing:plan (hub)
  └── test (sub-skill)
        └── rubysmithing-tester (agent)
```

## Step 1: Collect Target

Accept:
- File path to a Gemfile or `.gemspec`
- Directory path (scan for Gemfile, features/, Ruby files)
- No target → use current working directory

## Step 2: Run Verification

Delegate to `rubysmithing-tester` agent. The agent performs:

1. **Gem Existence** — curl RubyGems API for each gem
2. **Bundle Install** — isolated `bundle install` in temp directory
3. **Integration** — version conflict detection
4. **Convention Compliance** — rubocop scan
5. **Cucumber** — run scenarios if `features/` present

## Step 3: Format Output

The agent produces a structured verification report. Present it to the user with a clear VERDICT banner.

## Step 4: Route based on verdict

- **PASS**: inform user verification succeeded, artifact ready for auditor
- **FAIL**: list the `ISSUES FOR BUILDER RETRY` clearly so the Sovereign can re-dispatch