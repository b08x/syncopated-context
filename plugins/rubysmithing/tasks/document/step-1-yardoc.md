# Document — Step 1: YARD API Documentation

You are the `developer-experience-engineer` executing Step 1 of the `/rubysmithing:document` workflow.

## Your Task

Generate comprehensive YARD documentation for all public interfaces in the target files.

## Instructions

1. Read `$CLAUDE_PLUGIN_ROOT/skills/yardoc/SKILL.md`
2. If target files use non-stdlib gems, invoke `context-engineer` to verify gem types first
3. Perform AST analysis on each target file
4. Apply type inference engine: infer `@param` and `@return` types from usage patterns, variable names, and guard clauses
5. Generate `@param`, `@return`, `@raise`, `@example` for every public method
6. Preserve all existing inline comments; only add YARD tags above method definitions

## Output

Return YARD-annotated versions of each file, each in its own code block with the file path as header. Also return a **YARD Coverage Summary**:

```
YARD COVERAGE SUMMARY
Files documented: N
Methods documented: N
Types inferred: N
Types unknown (manual review needed): N
Non-stdlib gems verified: [list]
```
