---
description: Generate comprehensive YARD documentation for a Ruby file using semantic AST analysis and type inference.
argument-hint: "<file-path>"
allowed-tools: ["Read", "Write", "Grep", "Glob"]
---

Generate YARD documentation for the target Ruby file. Load and follow all instructions from:
`$CLAUDE_PLUGIN_ROOT/skills/rubysmithing-yardoc/SKILL.md`

**Detect target from arguments:**

- File path → document that file
- No argument → ask: "Which Ruby file should I document?"

**Prerequisite check (run before generating type annotations):**

Read the target file first. If it uses non-stdlib gems (check imports/requires), invoke the context cache:

```bash
ruby $CLAUDE_PLUGIN_ROOT/skills/rubysmithing-context/scripts/context_cache.rb check <gem-name> --json
```

Use verified method signatures for `@param` and `@return` type annotations. If cache misses, resolve via Context7 MCP first (use `mcp__plugin_context7_context7__resolve-library-id` then `mcp__plugin_context7_context7__query-docs`).

**Follow all steps in the skill:**

1. Validate target file — verify `.rb` extension, parse for syntax validity
2. Check `.yardopts` and existing documentation patterns for consistency
3. Semantic code analysis — AST structure, type inference, behavioral patterns
4. Generate complete YARD comment blocks: `@param`, `@return`, `@example`, `@raise`, `@since`, `@see`
5. Quality assurance — validate types, examples, YARD compliance
6. Insert documentation, output quality report summary

Generate realistic working examples. Use precise Ruby types. Never use vague or placeholder types like `Object` when specific types are inferable.
