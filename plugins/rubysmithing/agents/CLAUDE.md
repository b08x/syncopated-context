# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is the **agents directory** of the rubysmithing plugin v2.2.0. It contains the consolidated **1+3 architecture** — 1 Orchestrator and 3 specialized Sub-agents. These agents implement the sovereign execution model for the entire plugin.

## Agent Architecture (1+3 Model)

### Orchestrator
- **Sovereign** (`rubysmithing-sovereign`): The single entry point. Detects conventions, resolves context, and dispatches to sub-agents. Consolidates routing and quality governance.

### Sub-agents
- **Builder** (`rubysmithing-builder`): The Executor. Responsible for all code generation (General, AI/NLP, TUI, Scaffolding, Data, DX).
- **Researcher** (`rubysmithing-researcher`): The Epistemic Verifier. Responsible for Gem API verification (Context7), foreign translation (Python/Go/React), and codebase mapping.
- **Auditor** (`rubysmithing-auditor`): The Fixer & Judge. Responsible for SIFT QA reports, root-cause diagnostics, refactoring, and "Do-and-Judge" evaluation.

## Agent File Structure

### Required Frontmatter

All agent files must include YAML frontmatter with these required fields:

```yaml
---
name: agent-name
description: Clear purpose statement (≤1024 chars, third person)
model: inherit
color: [red|yellow|blue|green|purple]
tools: ["Tool1", "Tool2", "Tool3"]
---
```

### Content Patterns

1. **Agent Identity Statement**: "You are {name} — {Role}. You embody the {Archetype} archetype: {traits}."
2. **Core Responsibilities**: Primary scope of the consolidated role.
3. **Operational Protocol**: Step-by-step instructions for the agent's workflow.
4. **Output Format**: Specific templates for results.

## Agent Interaction Patterns

### The Sovereign Loop
1. **Sovereign** surveys the environment.
2. **Sovereign** dispatches **Researcher** for any missing gem API context.
3. **Sovereign** dispatches **Builder** for implementation.
4. **Sovereign** dispatches **Auditor** to evaluate/audit the output.
5. **Auditor** provides feedback to **Builder** if retry is needed.

## Testing and Validation

### Empirical Testing
Claims of "higher fidelity" must be verified through the test cases defined in `$CLAUDE_PLUGIN_ROOT/plans/1-plus-3-consolidation.md`:
- Test Case 1: Complex Compound Generation (RAG + TUI).
- Test Case 2: Deep Diagnostic & Repair (Zeitwerk circular dependencies).

## Integration with Plugin Ecosystem

### Shared Resources
Agents reference shared resources via absolute paths:
- `$CLAUDE_PLUGIN_ROOT/references/` - Shared patterns (genai, tui, design, refactor).
- `$CLAUDE_PLUGIN_ROOT/scripts/` - context_cache.rb (SQLite cache).

### Quality Gates
- **SIFT Protocol**: Conducted by the Auditor.
- **Do-and-Judge**: Sovereign sets the spec; Auditor acts as Judge.
- **Epistemic Verification**: Researcher verifies all gem APIs before code is written.

## Maintenance

### Archive
Archived specialized agents live in `archive/`. Do not use them for active workflows. Refer to them only for capturing legacy constraints during architectural evolution.
