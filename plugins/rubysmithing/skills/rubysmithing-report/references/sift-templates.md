# SIFT Response Templates

Two hotkey-activated response modes for focused analysis.
Load this file when the user triggers either template explicitly or by intent.

## Contents
- [System Design Review template](#hotkeyquotsystem-design-reviewquot)
- [Backlog template](#hotkeyquotbacklogquot)
- [Tech Advisory template](#hotkeyquottech-advisoryquot)

---

## [hotkey="system design review"]

### Instructions for Structured System/Component Review

Analyze the provided information (requirements, current design, proposed changes) using
EXACTLY the following format. Infuse analysis with the **Rubysmith Pragmatist's**
technically-grounded perspective, strictly evaluating DI, functional pipelines, and state isolation.

---

#### Core Assessment

- Include 4–6 bullet points summarizing the most critical findings
- Each bullet: 1–3 sentences
- Focus: key strengths, weaknesses, risks, major recommendations
- Include direct citations to specific requirements or design documents in parentheses
- First bullet: overall impression of the current state or proposal
- Final bullets: key go-forward actions or decisions

---

#### Expanded Analysis

Answer each question below in the specified format. Include direct citations throughout.

**What is the stated goal or problem this system/component addresses?**
Write 1–2 paragraphs describing the primary purpose, scope, and key functionalities.

**What are the key strengths of the current design/proposal?**
Write 1 paragraph identifying positive aspects (e.g., strict adherence to endless methods,
clean monadic flow). Provide specific examples and cite evidence.

**What are the primary concerns or weaknesses identified?**
Write 1–2 paragraphs detailing identified issues (e.g., pipeline blocks exceeding cap of 3,
missing constructor DI, rescue of StandardError instead of monads). Be specific and cite
the problematic areas. Apply Rubysmith Pragmatist parallels where they illuminate concerns.

**What are the major risks associated with this system/component or proposal?**
List 3–5 key risks (technical, operational, security, etc.) as bullet points.
For each: briefly describe potential impact and likelihood.

**What recommendations are made to address concerns and mitigate risks?**
Provide 3–5 actionable recommendations as bullet points. Each should be specific and
aim to improve the design toward full Rubysmith compliance.

**What is the larger architectural or project context?**
List 5–10 relevant keywords or short phrases (e.g., Command Pattern, dry-monads,
RSpec verifying doubles, Zeitwerk autoloading) that place this component in its
broader technical environment.

---

*Maintain strict adherence to this format, including all section headers, question formatting,
and citation style.*

---

## [hotkey="backlog"]

### Instructions for Backlog Generation

Create a project backlog **based on the System Design Review findings**. If a system design
review was not already produced in this session, **first generate one** using the
`[hotkey="system design review"]` template, then extract backlog items from it.

You must generate **two markdown files** in the project folder:
- `.backlog/stories.md`
- `.backlog/tasks.md`

Use the exact file headings and formats below. Ensure each task references a story ID.

**Format requirements:**
- Stories must follow the user story template: `As a [role], I want [capability], so that [benefit].`
- Each story includes acceptance criteria bullets.
- Tasks must be granular, implementation-ready, and mapped to a story ID.
- Use consistent IDs: `US-001`, `US-002`, ... and `T-001`, `T-002`, ...
- If a story depends on another, note it in a `Dependencies:` line.

**Output format (exactly):**
```
FILE: .backlog/stories.md

# Backlog — User Stories

## US-001 — [Short title]
As a [role], I want [capability], so that [benefit].
Acceptance Criteria:
* ...
* ...
Dependencies: [US-### or None]

## US-002 — [Short title]
As a [role], I want [capability], so that [benefit].
Acceptance Criteria:
* ...
* ...
Dependencies: [US-### or None]
```

```
FILE: .backlog/tasks.md

# Backlog — Tasks

## T-001 — [Short title]
Story: US-001
Details:
* ...
* ...

## T-002 — [Short title]
Story: US-002
Details:
* ...
* ...
```

*Maintain strict adherence to this format and file labeling.*

---

## [hotkey="tech advisory"]

### Instructions for Tech Advisory

1. Run a condensed system/component review applying the Rubysmith Pragmatist perspective
2. Then write a **very short technical advisory**:
   - **Hard limit: 700 characters** (count carefully)
   - **2–5 supporting links** in bare link format (no markdown link syntax)
   - Focus exclusively on **critical issues** needing immediate attention:
     - God classes
     - Global monkey-patches
     - Failing test coverage
     - Missing circuit breakers on external API calls
     - Unguarded pipeline execution
     - Security vulnerabilities
   - Issues relevant to: system stability, security, or core functionality only

**Format:**
```
ADVISORY — [component/system name] — [date]

[700 characters max of critical findings and immediate actions]

Links:
https://...
https://...
```
