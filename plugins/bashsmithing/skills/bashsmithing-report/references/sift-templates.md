# SIFT Response Templates

Two hotkey-activated response modes for focused analysis.
Load this file when the user triggers either template explicitly or by intent.

---

## [hotkey="system design review"]

### Instructions for Structured System/Component Review

Analyze the provided information (requirements, current design, proposed changes) using
EXACTLY the following format. Infuse analysis with the **Bashsmith Pragmatist's**
technically-grounded perspective, strictly evaluating functional encapsulation, state
isolation, and robust error trapping (`set -euo pipefail`).

---

#### Core Assessment

- Include 4 to 6 bullet points summarizing the most critical findings
- Each bullet: 1 to 3 sentences
- Focus: key strengths, weaknesses, risks, major recommendations
- Include direct citations to specific requirements or design documents in parentheses
- First bullet: overall impression of the current state or proposal
- Final bullets: key go-forward actions or decisions

---

#### Expanded Analysis

Answer each question below in the specified format. Include direct citations throughout.

**What is the stated goal or problem this system/component addresses?**
Write 1 to 2 paragraphs describing the primary purpose, scope, and key functionalities.

**What are the key strengths of the current design/proposal?**
Write 1 paragraph identifying positive aspects (e.g., 100% Shellcheck clean,
robust functional encapsulation, clean subshell isolation). Cite evidence.

**What are the primary concerns or weaknesses identified?**
Write 1 to 2 paragraphs detailing identified issues (e.g., global state pollution,
unquoted variable expansions, reliance on external tools without path checks,
missing `set -e` guards). Apply Bashsmith Pragmatist parallels where they
illuminate concerns.

**What are the major risks associated with this system/component or proposal?**
List 3 to 5 key risks (technical, operational, security, etc.) as bullet points.
For each: briefly describe potential impact and likelihood.

**What recommendations are made to address concerns and mitigate risks?**
Provide 3 to 5 actionable recommendations as bullet points. Each should be specific and
aim to improve the design toward full Bashsmith compliance.

**What is the larger architectural or project context?**
List 5 to 10 relevant keywords or short phrases (e.g., Functional Encapsulation,
BATS testing, return monads, subshell isolation, associative arrays) that place
this component in its broader technical environment.

---

*Maintain strict adherence to this format, including all section headers, question formatting,
and citation style.*

---

## [hotkey="tech advisory"]

### Instructions for Tech Advisory

1. Run a condensed system/component review applying the Bashsmith Pragmatist perspective
2. Then write a **very short technical advisory**:
   - **Hard limit: 700 characters** (count carefully)
   - **2 to 5 supporting links** in bare link format (no markdown link syntax)
   - Focus exclusively on **critical issues** needing immediate attention:
     - Global state pollution (missing `local`)
     - Insecure `eval` or command injection
     - Unquoted variables leading to globbing/splitting
     - Missing `set -euo pipefail` in core logic
     - Monolithic scripts lacking functional isolation
     - Resource leaks (unclosed file descriptors)
   - Issues relevant to: system stability, security, or core functionality only

**Format:**
```
ADVISORY : [component/system name] : [date]

[700 characters max of critical findings and immediate actions]

Links:
https://...
https://...
```
