---
description: Full SIFT Protocol QA audit with structured rubric evaluation. Runs SIFT assessment (senior-qa-engineer) → rubric generation (director-of-ai-risk) → compliance evaluation (compliance-guardrail-agent).
argument-hint: "<path-or-directory>"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Agent"]
---

Run the `/rubysmithing:audit` workflow on the target provided in the arguments.

## Step 1 — SIFT Assessment

Dispatch the `senior-qa-engineer` agent with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/audit/step-1-report.md`
- Target: the path or directory from arguments

Wait for the complete SIFT report and Artifact Summary before proceeding.

## Step 2 — Rubric Generation

Dispatch the `director-of-ai-risk` agent with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/audit/step-2-meta-judge.md`
- SIFT report and Artifact Summary: complete output from Step 1

Wait for the scratchpad path and rubric summary before proceeding.

## Step 3 — Compliance Evaluation

Dispatch the `compliance-guardrail-agent` with:

- Task instructions: `$CLAUDE_PLUGIN_ROOT/tasks/audit/step-3-judge.md`
- Scratchpad path: from Step 2
- Artifact files: from Step 1 Artifact Summary

## Final Output

Present:
1. SIFT report summary (Step 1 key findings)
2. Rubric dimensions and weights (Step 2)
3. Complete compliance evaluation with PASS/FAIL verdict (Step 3)
