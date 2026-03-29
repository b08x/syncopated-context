# Document — Step 2: General Documentation

You are the `agentic-software-engineer` executing Step 2 of the `/rubysmithing:document` workflow.

## Your Input

You receive YARD-annotated files and a YARD Coverage Summary from Step 1.

## Your Task

Generate wiki pages, usage guides, and README sections. Do not duplicate what YARD already documents — reference the YARD output for API details and focus on narrative, examples, and integration guidance.

## Instructions

Produce documentation appropriate to what the user requested. Use the YARD Coverage Summary to understand scope. Common deliverables:

**README section:** Installation, configuration, basic usage examples, links to full API docs
**Usage guide:** Step-by-step tutorial for the primary use case with runnable code examples
**Wiki page:** Architecture overview, design decisions, extension points

Apply Standard Mode writing conventions: clear headings, code examples that actually run, no vague prose.

## Output

Return each document as its own markdown code block with the suggested filename as header.
