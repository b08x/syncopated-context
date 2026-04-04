# Artifacts Generation Guide

Specifications for generating deliverable artifacts from interview prep sessions.
Artifacts are generated only when the interaction has produced enough substance, or
when the user explicitly requests one.

## Artifact Types

### 1. Resume Rewrite (.docx)

**Trigger:** Recruiter persona completes an AUDIT_MODE gap analysis, or user requests
"rewrite my resume" / "give me the optimized version."

**Generation process:**

1. Read the docx skill at `/mnt/skills/public/docx/SKILL.md` for formatting guidance.
2. Apply all identified fixes from the gap analysis.
3. Structure the document with ATS-safe formatting:
   - Single column layout
   - Standard fonts (Calibri, Arial, or Georgia), 10-11pt body
   - Section headers: bold, 12-14pt, standard labels (Experience, Education, Skills, Projects)
   - No tables, graphics, text boxes, headers/footers, or multi-column layouts
   - Consistent date formatting (MMM YYYY) right-aligned
4. Rewrite each bullet using the Metric Conversion framework from recruiter.md.
5. Mirror exact JD keyword phrases in the Skills section and relevant bullets.
6. Save to `/mnt/user-data/outputs/` with filename pattern: `resume_optimized_[company].docx`

**Quality checks before delivery:**
- Every bullet passes the "So What" test
- All JD hard-skill keywords appear at least once
- No bullet exceeds 2 lines
- Summary/objective mirrors JD language
- Total length: 1 page (0-7 years experience) or 2 pages (8+ years)

### 2. Prep Checklist / Study Guide (.md)

**Trigger:** Strategist persona completes a JD decode, or user requests a study plan /
prep checklist / "what should I study?"

**Generation process:**

1. Extract all identified traps, shadow requirements, and critical vectors from the
   Strategist analysis.
2. Organize into a prioritized study guide with three tiers:

```markdown
# Interview Prep: [Company] — [Role]

## Priority 1: Must-Know (Interview Killers)
Topics that will definitely be tested based on JD analysis.
Each topic includes:
- The Trap (what they're really asking)
- The Fix (what to know cold)
- Study resources (1-2 specific links or concepts)
- Time estimate

## Priority 2: Likely Topics
High-probability areas based on company patterns and JD signals.
Same structure as Priority 1.

## Priority 3: Edge Cases
Lower probability but high-impact if they come up.
Brief descriptions only.

## Behavioral Prep
- Expected behavioral vectors based on JD cultural signals
- 2-3 "Safe Failure" story prompts to prepare
- The 5-level drill framework for each story

## Day-Of Checklist
- Technical environment setup (if live coding)
- Questions to ask the interviewer
- Red flags to avoid
```

3. Save to `/mnt/user-data/outputs/` with filename: `prep_checklist_[company]_[role].md`

### 3. Mock Interview Transcript with Scoring (.md)

**Trigger:** Interviewer persona completes a mock session (minimum 3 questions across
at least 2 vectors), or user requests "score me" / "how did I do?"

**Generation process:**

1. Compile the full mock exchange into a structured transcript.
2. Apply the Signal Assessment framework from interviewer.md.
3. Generate the document:

```markdown
# Mock Interview Transcript
**Role:** [Role from JD]
**Date:** [Date]
**Vectors Tested:** [List]

---

## Vector 1: [Topic]

**Q:** [Question as posed]
**A:** [User's response — summarized, not verbatim]
**Signal:** [Strong / Moderate / Weak / No Signal]
**Assessment:** [1-2 sentence evaluation of what was strong/missing]
**Probe Depth Reached:** [Level 1-4 of escalation]

[Repeat for each Q&A exchange]

---

## Vector 2: [Topic]
[Same structure]

---

## Signal Report

| Vector | Signal Level | Key Observation |
|--------|-------------|-----------------|
| [V1]   | [Level]     | [Note]          |
| [V2]   | [Level]     | [Note]          |
| [V3]   | [Level]     | [Note]          |

**Overall Assessment:** [Hire / Lean Hire / Lean No Hire / No Hire]

## Critical Gaps (Study These)
→ [Gap]: [Specific study recommendation]
→ [Gap]: [Specific study recommendation]

## Strengths (Lean Into These)
→ [Strength]: [How to leverage in real interview]
→ [Strength]: [How to leverage in real interview]

## Recommended Next Steps
1. [Specific action]
2. [Specific action]
3. [Specific action]
```

4. Save to `/mnt/user-data/outputs/` with filename: `mock_transcript_[company]_[role].md`

## General Artifact Principles

- Always present artifacts using the `present_files` tool after generation.
- Keep the post-artifact message minimal — the artifact speaks for itself.
- If the user hasn't provided enough information for a complete artifact (e.g., no JD
  for a prep checklist), state what's missing and request it before generating.
- Artifacts should be standalone — readable and useful without the conversation context.
