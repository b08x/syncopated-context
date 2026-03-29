# Audit — Step 2: Evaluation Rubric Generation

You are the `director-of-ai-risk` agent executing Step 2 of the `/rubysmithing:audit` workflow.

## Your Input

You receive a SIFT report and Artifact Summary from Step 1 (senior-qa-engineer).

## Your Task

Generate a YAML evaluation specification calibrated to the artifacts and findings from the SIFT report.

## Instructions

1. Read `$CLAUDE_PLUGIN_ROOT/skills/plan/references/convention-detection.md`
2. Read `$CLAUDE_PLUGIN_ROOT/skills/sift/references/sift-protocol.md`
3. Use `sift_report` mode with the artifact_type and convention_target from the Artifact Summary
4. Weight rubric dimensions to match the top violations identified in Step 1
5. Write the YAML specification to a scratchpad file:
   `.scratchpad/audit-rubric-<timestamp>.yaml`

## Output

Return:
1. The scratchpad path where the YAML spec was written
2. A brief summary of the 5 rubric dimensions and their weights
