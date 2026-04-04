---
name: ruby-design-patterns
description: Explain, compare, and apply Ruby design patterns using bundled pattern notes. Helps choose patterns, refactor code, translate patterns to Ruby idioms, and learn tradeoffs.
license: MIT
allowed-tools: Read Edit Grep Glob Bash
metadata:
  author: b08x
  version: "1.0.0"
  category: developer-tools
---

# Ruby Design Patterns

## Overview

Use the local Ruby design-pattern notes to recommend, explain, or refactor patterns with Ruby-idiomatic examples.

## Workflow

1. Clarify the goal, constraints, and code context (OO vs functional style, metaprogramming tolerance, performance, testability).
2. Identify candidate patterns and select the best fit; state why.
3. Load `references/patterns-index.md` to find the right note.
4. Load the chosen pattern note(s) and follow their problem, solution, and example structure.
5. Produce the response for the requested task.

## Resource Use

- Use `references/patterns-index.md` to locate pattern notes.
- Prefer loading only the specific pattern note(s) needed.
- If the user asks about convention over configuration or DSLs, load those notes even though they are not classic GoF patterns.

## Response Guidance

- For explanations, cover the problem, solution, pros and cons, and when not to use the pattern.
- For refactors, show before and after or stepwise changes, and highlight Ruby idioms (modules, mixins, blocks, duck typing).
- For comparisons, provide a concise tradeoff table and a recommendation.
- Ask one targeted clarification only when the pattern choice depends on missing context.
