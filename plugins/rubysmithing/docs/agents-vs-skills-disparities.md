---
name: agents-vs-skills-disparities
description: Comprehensive comparison of rubysmithing v2.2.0 agents architecture vs v2.1.0 skills architecture, documenting structural evolution, functional mappings, protocol differences, and migration considerations.
version: 2.2.0
type: architecture-comparison
audience: plugin-developers, architects, maintainers
tags: [architecture, agents, skills, comparison, migration, rubysmithing]
---

# Agents vs Skills: Architecture Disparities Analysis

**Rubysmithing Plugin v2.1.0 → v2.2.0**

*Document Type: SFL Architecture Comparison*  
*Status: Draft*  
*Last Updated: 2025-01-XX*  
*Owner: rubysmithing-sovereign*

---

## Executive Summary

The rubysmithing plugin underwent a **major architectural consolidation** from v2.1.0 to v2.2.0, transitioning from a **hub-and-spoke skills model** (10 specialized skills) to a **1+3 sovereign agent model** (1 orchestrator + 3 sub-agents). This refactoring aimed to reduce coordination overhead, improve quality gate consistency, and centralize episteemic verification.

| Aspect | v2.1.0 (Skills) | v2.2.0 (Agents) | Delta |
|:-------|:---------------|:---------------|:------|
| **Architecture** | Hub-and-spoke (10 skills) | 1+3 model (Sovereign + 3) | Consolidation |
| **Entry Point** | `/rubysmithing:plan` | `rubysmithing-sovereign` | Unified |
| **Delegation** | Skill-to-skill via plan | Agent-to-sub-agent via Sovereign | Centralized |
| **QA Framework** | SIFT Protocol V1.0 | SIFT Protocol + Do-and-Judge | Enhanced |
| **Error Handling** | Error Contract System | `[AGENT ERROR]` blocks | Structured |
| **Version** | v2.1.0 | v2.2.0 | +0.1.0 |

---

## 1. Architecture Evolution

### 1.1 v2.1.0 Skills Architecture (Hub-and-Spoke)

```
┌─────────────────────────────────────────────────────────────┐
│                      PLAN (Hub Orchestrator)                    │
├────────────────┬────────────────┬────────────────┬────────────┤
│ analyse          │ context         │ data-engineer   │ genai      │
├────────────────┼────────────────┼────────────────┼────────────┤
│ refactor         │ scaffold        │ sift            │ tui        │
├────────────────┼────────────────┼────────────────┼────────────┤
│ yardoc           │                 │                 │            │
└────────────────┴────────────────┴────────────────┴────────────┘
```

**Characteristics:**
- 10 specialized skills with distinct responsibilities
- `plan` skill acts as central hub/router
- Direct invocation allowed for known domains
- Skills delegate to shared agents at `$CLAUDE_PLUGIN_ROOT/agents/` for complex operations
- Two-mode architecture: Lite Mode vs Standard Mode

**File Structure:**
```
skills/
├── analyse/
│   ├── SKILL.md
│   ├── commands/analyse.md
│   └── references/analyse-methods.md
├── context/SKILL.md
├── data-engineer/SKILL.md
├── genai/SKILL.md
├── plan/
│   ├── SKILL.md
│   ├── references/convention-detection.md
│   ├── references/conventions.md
│   └── references/error-contract.md
├── refactor/
│   ├── SKILL.md
│   ├── commands/refactor.md
│   └── references/refactor-patterns.md
├── scaffold/SKILL.md
├── sift/
│   ├── SKILL.md
│   ├── commands/report.md
│   ├── references/sift-protocol.md
│   └── references/sift-templates.md
├── tui/SKILL.md
├── yardoc/SKILL.md
└── CLAUDE.md
```

### 1.2 v2.2.0 Agents Architecture (1+3 Model)

```
┌─────────────────────────────────────────────────────────────┐
│                 rubysmithing-sovereign (Orchestrator)           │
├─────────────────────────┬─────────────────────┬───────────────┤
│ rubysmithing-researcher   │ rubysmithing-builder │  rubysmithing- │
│ (Epistemic Verifier)      │ (Executor)           │  auditor       │
│                           │                     │  (Fixer & Judge)│
└─────────────────────────┴─────────────────────┴───────────────┘
```

**Characteristics:**
- **1 Orchestrator**: `rubysmithing-sovereign` - surveys, resolves, dispatches, audits
- **3 Sub-agents**:
  - `rubysmithing-researcher` - Gem API verification, codebase survey, foreign translation
  - `rubysmithing-builder` - All code generation (General, AI/NLP, TUI, Data, DX, Scaffolding)
  - `rubysmithing-auditor` - SIFT audits, diagnostics, refactoring, evaluation
- Consolidated routing and quality governance
- Single entry point for all requests

**File Structure:**
```
agents/
├── rubysmithing-sovereign.md
├── rubysmithing-builder.md
├── rubysmithing-researcher.md
├── rubysmithing-auditor.md
└── CLAUDE.md
```

### 1.3 Key Architectural Shifts

| Dimension | v2.1.0 Skills | v2.2.0 Agents | Impact |
|:----------|:--------------|:--------------|:-------|
| **Entry Points** | Multiple (`/rubysmithing:plan`, `/rubysmithing:sift`, etc.) | Single (`rubysmithing-sovereign`) | Simplified routing |
| **Coordination** | Peer-to-peer delegation via plan | Hierarchical (Sovereign → Sub-agents) | Reduced overhead |
| **Scope** | Domain-specialized (10 skills) | Role-specialized (4 agents) | Consolidated responsibilities |
| **Quality Gates** | Distributed (each skill handles own QA) | Centralized (Sovereign enforce SIFT) | Consistent standards |
| **Context Resolution** | Ad-hoc per skill | Mandatory via Researcher | Zero-hallucination guarantee |

---

## 2. Functional Mappings

### 2.1 Direct Mappings

| v2.1.0 Skill | Primary Responsibility | v2.2.0 Agent | Mapping Notes |
|:--------------|:-----------------------|:-------------|:--------------|
| `analyse` | Diagnostics, debugging | `rubysmithing-auditor` | Diagnostic methods moved to Auditor |
| `context` | Gem API verification | `rubysmithing-researcher` | Direct 1:1 mapping |
| `data-engineer` | Schema design, data pipelines | `rubysmithing-builder` | Builder handles all generation including data |
| `genai` | AI/NLP integration | `rubysmithing-builder` | Builder handles AI/NLP domain |
| `refactor` | Convention compliance | `rubysmithing-auditor` | Audited refactoring via Auditor |
| `scaffold` | Project initialization | `rubysmithing-builder` | Builder handles scaffolding |
| `sift` | QA assessment | `rubysmithing-auditor` | SIFT protocol now in Auditor |
| `tui` | Terminal UI development | `rubysmithing-builder` | Builder handles TUI domain |
| `yardoc` | YARD documentation | `rubysmithing-builder` | Builder handles DX/documentation |
| `plan` | General code generation, orchestration | `rubysmithing-sovereign` | Orchestration moved to Sovereign |

### 2.2 Consolidation Map

```
┌─────────────────────────────────────────────────────────────┐
│                    rubysmithing-sovereign                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐│
│  │  plan (v2.1.0)   │  │   sift (v2.1.0) │  │ analyse (v2.1)││
│  │  - Orchestration │  │   - QA Framework │  │ - Diagnostics  ││
│  └────────┬────────┘  └────────┬────────┘  └───────┬───────┘│
│           │                      │                     │          │
│           └──────────────────────┼─────────────────────┘          │
│                                  ▼                                 │
│                    ┌─────────────────────┐                        │
│                    │ rubysmithing-auditor│←───────────────────────┘
│                    │ - SIFT Protocol     │
│                    │ - Diagnostics       │
│                    │ - Refactoring       │
│                    │ - Judge Role        │
│                    └─────────────────────┘                        │
│                                  │                                 │
│         ┌────────────────────────┼─────────────────────┐          │
│         ▼                            ▼                             ▼          │
│┌───────────────────┐    ┌───────────────────┐    ┌─────────────────┐│
││ rubysmithing-     │    │ rubysmithing-     │    │ rubysmithing-   ││
││ researcher        │    │ builder           │    │ auditor         ││
││ - context (v2.1)  │    │ - genai (v2.1)    │    │ - analyse (v2.1)││
││ - Gem API resolve │    │ - data-engineer   │    │ - refactor      ││
││ - Foreign trans.  │    │ - scaffold        │    │ - sift (v2.1)   ││
││ - Codebase survey │    │ - tui            │    │                 ││
│└───────────────────┘    │ - yardoc          │    └─────────────────┘│
│                          └───────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Responsibility Consolidation

| Agent | Consolidated Skills | Responsibility Scope |
|:------|:---------------------|:---------------------|
| **rubysmithing-sovereign** | `plan` | Orchestration, convention detection, quality gate enforcement, strategic dispatch |
| **rubysmithing-researcher** | `context` | Epistemic verification, gem API resolution, foreign codebase translation, codebase survey |
| **rubysmithing-builder** | `genai`, `data-engineer`, `scaffold`, `tui`, `yardoc`, `plan` (generation) | All code generation: AI/NLP, data pipelines, scaffolding, TUI, documentation, general code |
| **rubysmithing-auditor** | `analyse`, `refactor`, `sift`, `plan` (QA) | All quality tasks: diagnostics, SIFT audits, refactoring, do-and-judge evaluation |

---

## 3. Protocol Differences

### 3.1 Delegation Patterns

#### v2.1.0 Skills Delegation
```
User Request → plan skill → [identifies domain] → delegates to specialized skill
                           ↓
                    (direct invocation for known domains)
                           ↓
                 skill delegates to shared agents if needed
```

**Example Flow (v2.1.0):**
```
User: "Build a RAG pipeline"
  → plan skill detects: AI/NLP domain
  → plan delegates to genai skill
  → genai checks if context resolved
  → genai delegates to context skill for gem API verification
  → genai generates code
  → genai returns to user
```

#### v2.2.0 Agents Delegation
```
User Request → rubysmithing-sovereign
  ↓
[Layer 1: Survey] → Convention detection, dependency mapping
  ↓
[Layer 2: Resolve] → Dispatches to rubysmithing-researcher if needed
  ↓
[Layer 3: Dispatch] → Strategic delegation to sub-agents
  ↓
[Layer 4: Audit] → Quality gate via rubysmithing-auditor
  ↓
Result to user
```

**Example Flow (v2.2.0):**
```
User: "Build a RAG pipeline"
  → rubysmithing-sovereign surveys environment
  → detects non-stdlib gems (ruby_llm, pgvector)
  → dispatches to rubysmithing-researcher for API verification
  → Sovereign receives verified signatures
  → Sovereign dispatches to rubysmithing-builder for implementation
  → Builder generates code
  → Sovereign dispatches to rubysmithing-auditor for SIFT assessment
  → Auditor provides score
  → If FAIL: Sovereign re-dispatches to Builder with retry prompt
  → If PASS: Sovereign delivers final result to user
```

### 3.2 Error Handling

#### v2.1.0: Error Contract System
- Defined in `skills/plan/references/error-contract.md`
- Agents return `[AGENT ERROR]` blocks rather than bare failures
- Structured error propagation enables retry logic
- Separation of concerns between orchestration and execution

#### v2.2.0: Agent Error Blocks
- Sub-agents return `[AGENT ERROR]` blocks
- Sovereign merges `coverageGaps` and makes final "Retry or Annotate" decision
- Same pattern name, different implementation context

**Comparison:**
```
┌─────────────────────┐  ┌─────────────────────┐
│ v2.1.0 Error        │  │ v2.2.0 Error        │
│                     │  │                     │
│ [AGENT ERROR]       │  │ [AGENT ERROR]       │
│ skill: context      │  │ agent: researcher    │
│ error: timeout      │  │ error: timeout      │
│ coverageGaps: [...]  │  │ coverageGaps: [...]  │
│ retry: true         │  │ retry: true         │
└─────────────────────┘  └─────────────────────┘
  Similar structure     Similar structure
  but skill-based         but agent-based
```

### 3.3 Quality Gates

#### v2.1.0: Distributed QA
- Each skill responsible for own quality checks
- SIFT protocol implemented in `sift` skill
- Refactoring in `refactor` skill
- Analyse methods in `analyse` skill
- No centralized enforcement

#### v2.2.0: Centralized Quality Gates
- **Sovereign consolidates all quality assurance**
- Integrated SIFT Protocol via Auditor
- Do-and-Judge Loop for critical implementations
- Mandatory verification before delivery

**Quality Gate Sequence (v2.2.0):**
```
1. Architectural Review → rubysmithing-auditor (full SIFT Protocol report)
2. Do-and-Judge Loop → Sovereign sets rubric, Auditor acts as Judge
3. Closing the Loop → If Auditor fails, re-dispatch to Builder
4. Post-Dispatch Evaluation → Coverage, Consistency, Integrity checks
```

### 3.4 Operational Protocols

| Protocol Aspect | v2.1.0 Skills | v2.2.0 Agents |
|:----------------|:--------------|:--------------|
| **Entry Statement** | None standardized | Sovereign Decision (Mode, Convention, Verification, Strategy, Quality Gate) |
| **Pre-flight Check** | Ad-hoc per skill | Mandatory survey (Convention Detection, Dependency Mapping, Architecture Mapping) |
| **Context Resolution** | Optional, per skill | Mandatory via Researcher, Zero-hallucination requirement |
| **Dispatch Strategy** | Domain-based routing | Strategic (Parallel for independent, Sequential for dependent) |
| **Post-Delivery** | Skill-specific | Integrated gates (Coverage, Consistency, Integrity) |

---

## 4. Convention Detection

### 4.1 Detection Cascade (Both Versions)

Both versions implement the same detection priority:

```
1. .rubocop.yml present → RuboCop config
2. standard in Gemfile → StandardRB
3. .rubysmith / rubysmith gem → Rubysmith defaults
4. None → community idioms / Rubysmith architectural standards
```

### 4.2 Implementation Differences

#### v2.1.0 (Skills)
- Defined in `skills/plan/references/convention-detection.md`
- Each skill performs own detection or inherits from plan
- `plan` skill acts as canonical source
- Detection documented in skill output

#### v2.2.0 (Agents)
- **Sovereign performs all convention detection** in Layer 1: The Survey
- Centralized in `rubysmithing-sovereign`
- Results flow to all sub-agents
- Single source of truth for entire session

---

## 5. Mode Handling

### 5.1 Lite Mode

| Aspect | v2.1.0 | v2.2.0 | Notes |
|:-------|:------|:------|:------|
| **Trigger** | "quick script", "stdlib only", single file ≤50 lines | Same | No change |
| **Constraints** | Pure Ruby stdlib, no external gems | Same | No change |
| **Output** | Single file, minimal dependencies | Same | No change |

### 5.2 Standard Mode

| Aspect | v2.1.0 | v2.2.0 | Notes |
|:-------|:------|:------|:------|
| **Trigger** | Default for multi-file, complex tasks | Same | No change |
| **Requirements** | frozen_string_literal, Zeitwerk compliance | Same + Async, circuit_breaker, journald-logger | Expanded |
| **Stack** | Full convention stack | Same | No change |

---

## 6. Shared Resources & Referencing

### 6.1 Resource Locations

#### v2.1.0 Skills
```
$CLAUDE_PLUGIN_ROOT/agents/           # 13 specialized agents
$CLAUDE_PLUGIN_ROOT/references/       # Shared documentation
$CLAUDE_PLUGIN_ROOT/scripts/          # SQLite cache CLI
$CLAUDE_PLUGIN_ROOT/assets/           # TUI skeletons

skills/<name>/references/             # Skill-specific docs
skills/<name>/commands/               # Skill workflows
```

#### v2.2.0 Agents
```
$CLAUDE_PLUGIN_ROOT/references/       # Shared patterns (genai, tui, design, refactor)
$CLAUDE_PLUGIN_ROOT/scripts/          # context_cache.rb (SQLite cache)

# Agent-specific references (via absolute paths)
$CLAUDE_PLUGIN_ROOT/skills/scaffold/SKILL.md
$CLAUDE_PLUGIN_ROOT/references/genai-patterns.md
$CLAUDE_PLUGIN_ROOT/references/tui-patterns.md
$CLAUDE_PLUGIN_ROOT/references/design-patterns.md
$CLAUDE_PLUGIN_ROOT/skills/data-engineer/SKILL.md
```

### 6.2 Reference Evolution

| Resource | v2.1.0 | v2.2.0 | Status |
|:---------|:------|:------|:-------|
| gems-inventory.csv | `$CLAUDE_PLUGIN_ROOT/references/` | Same | Retained |
| error-contract.md | `skills/plan/references/` | Integrated into agents | Migrated |
| refactor-patterns.md | `skills/refactor/references/` | Same | Retained |
| sift-protocol.md | `skills/sift/references/` | Used by Auditor | Retained |
| analyse-methods.md | `skills/analyse/references/` | Used by Auditor | Retained |
| convention-detection.md | `skills/plan/references/` | Centralized in Sovereign | Migrated |

### 6.3 Context Caching

**Both versions** use the same SQLite cache mechanism:
```bash
ruby $CLAUDE_PLUGIN_ROOT/scripts/context_cache.rb fetch GEMNAME --json
ruby $CLAUDE_PLUGIN_ROOT/scripts/context_cache.rb store GEMNAME CONTEXT7_ID 'signatures' 'example'
```

**Location:** `~/.rubysmithing/context_cache.db`

**v2.2.0 Enhancement:**  Researcher explicitly manages cache as part of mandate with degradation protocol: Tier 1 (stale cache) → Tier 2 (gems-inventory.csv) → Tier 3 (`[AGENT ERROR]`)

---

## 7. Output Format Changes

### 7.1 v2.1.0 Skills Output

**plan skill:**
1. File path (relative to project root)
2. Complete file content
3. Rationale (one sentence per non-obvious decision)
4. Gemfile additions (if applicable)
5. Mode applied

**sift skill:** 8-section SIFT Protocol format with evidence framework

**analyse skill:** METHOD, TARGET, CONVENTION TARGET, Findings, ACTIONABLE NEXT STEPS

**refactor skill:** Pre-refactor audit, Complete refactored file, Change log, Behavioral changes, Mode applied

### 7.2 v2.2.0 Agents Output

**rubysmithing-sovereign:**
1. Sovereign Decision Statement (Mode, Convention, Verification, Strategy, Quality Gate)
2. Delegated results from sub-agents
3. Post-dispatch evaluation results

**rubysmithing-builder:**
1. Sovereign Decision Statement (inherited)
2. File Path
3. Complete File Content
4. Rationale
5. Gemfile Additions

**rubysmithing-researcher:**
1. Research Summary
2. Verified Signatures
3. Minimal Example
4. Paradigm Notes (if translating)
5. Handoff statement to Builder

**rubysmithing-auditor:**
- SIFT: 8-section format with Verification Footer
- Diagnostics: Method → Keyed Findings → Actionable Next Steps
- Refactoring: Pre-refactor Audit → Refactored Content → Change Log → Verification Status
- Judge: Score (1-5, default 2) → PASS/FAIL → RETRY_PROMPT

### 7.3 Key Format Differences

| Aspect | v2.1.0 | v2.2.0 |
|:-------|:------|:------|
| Decision Statement | None | Mandatory Sovereign Decision |
| Evidence Requirements | SIFT only | All quality assessments require file:line evidence |
| Scoring Default | Not specified | Default to 2 (scores above 2 require cited evidence) |
| Verdict Format | Various | PASS/FAIL with RETRY_PROMPT |

---

## 8. Integration Points

### 8.1 External Integrations
- **Context7 MCP** - Gem API verification (both versions)
- **Ruby stdlib** - Core Ruby functionality (both versions)
- **Project conventions** - RuboCop, StandardRB, Rubysmith (both versions)

**v2.2.0 Specific:** Zero-hallucination requirement - All non-stdlib gem usage must be verified

### 8.2 Internal Dependencies

**v2.1.0:** plan → all other skills, skills delegate to shared agents

**v2.2.0:** Sovereign → Researcher, Builder, Auditor; each agent has specific resource dependencies

### 8.3 Shared Resource Access
- **v2.1.0:** Skills access shared resources directly
- **v2.2.0:** Agents access via Sovereign or through absolute paths

---

## 9. Migration Guide

### 9.1 Breaking Changes

| Change | Impact | Migration |
|:-------|:-------|:----------|
| Single entry point | `/rubysmithing:plan` → `rubysmithing-sovereign` | Update all invocations |
| Consolidated agents | 10 skills → 4 agents | Map old calls to agents |
| Mandatory verification | Optional → Required | Ensure Researcher active |
| Centralized QA | Distributed → Centralized | Results pass through Auditor |

### 9.2 Migration Path

1. Update all plugin invocations from `/rubysmithing:<skill>` to `rubysmithing-sovereign`
2. Map skill-specific functionality:
   - Generation → Builder (via Sovereign)
   - QA → Auditor (via Sovereign)
   - Research → Researcher (via Sovereign)
3. Update custom workflows to use 1+3 model

### 9.3 Compatibility

- **Context cache:** ✅ Seamless continuity
- **Convention detection:** ✅ Improved
- **Gem API verification:** ✅ Enhanced
- **Error recovery:** ✅ Centralized

---

## 10. Summary

### 10.1 Architecture Evolution
| Dimension | v2.1.0 | v2.2.0 |
|:----------|:-------|:-------|
| Components | 10 skills + 13 agents | 4 agents |
| Architecture | Hub-and-spoke | 1+3 sovereign |
| Entry Points | Multiple | Single |
| Coordination | Distributed | Centralized |

### 10.2 Functional Consolidation
| Function | v2.1.0 | v2.2.0 |
|:---------|:------|:------|
| All Generation | Multiple skills | rubysmithing-builder |
| All QA | Multiple skills | rubysmithing-auditor |
| All Verification | context skill | rubysmithing-researcher |
| Orchestration | plan skill | rubysmithing-sovereign |

### 10.3 Quality Improvements
| QoS Aspect | v2.1.0 | v2.2.0 | Improvement |
|:-----------|:------|:------|:------------|
| Zero-hallucination | Optional | Mandatory | High |
| Quality consistency | Variable | Consistent | High |
| Context resolution | Ad-hoc | Mandatory | High |
| Coordination overhead | High | Low | High |

---

## Appendix: File Manifest

**v2.1.0 Skills:** analyse, context, data-engineer, genai, plan, refactor, scaffold, sift, tui, yardoc (10 skills)

**v2.2.0 Agents:** rubysmithing-sovereign, rubysmithing-builder, rubysmithing-researcher, rubysmithing-auditor (4 agents)

---

## Document Metadata

```yaml
schema: SFL
version: 1.0
type: architecture-comparison
authority: rubysmithing-sovereign
created: 2025-01-XX
status: draft
tags: [architecture, comparison, migration, agents, skills]
```

*This document follows SFL conventions. For updates, submit PRs to the rubysmithing plugin repository.*