# agent commands

Claude Code command definitions. Each `.md` file is a command that activates on trigger phrases. Defines behavior. Not implementation.

## Structure

```
commands/
├── *.md                  # Command definitions
│   ├── commit.md         # Git commit workflow
│   ├── docs.md          # Documentation generation
│   ├── implement.md     # Feature implementation
│   ├── refactor.md      # Code refactoring
│   ├── test.md          # Test-driven development
│   └── review.md        # PR/code review
└── gemini/              # Gemini CLI integration
    ├── project/         # Project-specific configs
    └── react/           # React tool configs
```

## Commands

| Command | Triggers | What It Does |
|---------|----------|--------------|
| commit | "commit", "commit changes" | Atomic commits with conventional messages |
| docs | "generate docs", "document" | Auto-generate docs from code |
| implement | "implement", "add feature" | TDD workflow—tests first |
| refactor | "refactor", "clean up" | AST-aware refactoring |
| test | "write tests", "add tests" | Test-driven development |
| review | "review", "code review" | PR review, feedback |

## Conventions

**File Structure:**
```markdown
# Command Name

## Triggers
- "trigger phrase 1"
- "trigger phrase 2"

## Workflow
Step-by-step instructions...

## Anti-Patterns
- What NOT to do
```

**NEVER Rules:**

- Never commit unless explicitly requested
- Never push to remote unless asked
- Never skip hooks
- Never use git `-i` flag

## Anti-Patterns

- Commands define behavior, not implementation
- No implementation logic in command files
- Don't duplicate—extract to shared

## Command vs Skill

- **Commands**: Behavior guidelines—what the agent should do
- **Skills**: Implementation capabilities—how the agent does it

## Gemini Integration

Subdirectory contains `.toml` configs for Gemini CLI tool definitions.
