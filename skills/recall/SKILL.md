---
name: recall
description: Multi-platform AI harness session recall across Claude Code, Gemini CLI, OpenCode, and Hermes. Correlates GitHub activity and backup changes. Handles temporal queries and cross-platform session aggregation with intelligent contextual chunking.
license: MIT
allowed-tools: Read Edit Grep Glob Bash Write
metadata:
  author: b08x
  version: "1.1.0"
  category: productivity
---

# Multi-Platform Recall

Comprehensive AI harness session recall across Claude Code, Gemini CLI, OpenCode, and Hermes, plus **Obsidian notes** and **Local Git activity** across your workspace. Every recall ends with the **One Thing** - a concrete, highest-leverage next action synthesized from cross-platform results.

## Architecture Overview

The system is built as a modular Python package (`recall/`) that enforces strict separation of concerns between data models, provider-specific extraction, AI analysis, and core orchestration.

### Package Structure

- **`recall/models.py`**: Unified dataclasses (`ParsedSession`, `ParsedMessage`, `SessionUsage`, etc.) ensuring schema consistency across all platforms.
- **`recall/providers/`**: Platform-specific extractors (Gemini, Hermes, Claude Code, OpenCode, Obsidian, Local Git) inheriting from a common `BaseProvider`.
- **`recall/ai/`**: 
    - `signatures.py`: DSPy signatures for semantic analysis.
    - `modules.py`: DSPy modules for topic extraction and timeline synthesis.
    - `chunking.py`: **Contextual Chunking Strategy** for handling long sessions.
- **`recall/core.py`**: Orchestrates providers and AI processing into a unified timeline.
- **`scripts/recall_cli.py`**: Unified entry point for all operations.

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Claude Code    │     │   Gemini CLI     │     │    Hermes       │
│  JSONL files    │     │   JSON files     │     │   SQLite DB    │
└────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
         │                       │                         │
         ▼                       ▼                         ▼
    ┌───────────────────────────────────────────────────────────┐
    │                RECALL PROVIDERS (Modular)                 │
    │       (Normalizes data to ParsedSession/ParsedNote)       │
    └────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
    ┌───────────────────────────────────────────────────────────┐
    │               CONTEXTUAL CHUNKING LAYER                   │
    │      (Intelligent message grouping for LLM context)       │
    └────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
    ┌───────────────────────────────────────────────────────────┐
    │               DSPy CORRELATION & ANALYSIS                 │
    │      (Timeline Synthesis + One Thing Generation)          │
    └────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
    ┌───────────────────────────────────────────────────────────┐
    │               OUTPUTS (CLI, JSON, Obsidian)               │
    └───────────────────────────────────────────────────────────┐
```

## Key Features

- **Multi-platform aggregation**: Correlates sessions from all major AI tools.
- **Contextual Chunking**: Intelligently groups messages based on temporal gaps (>30 mins) and semantic boundaries (user directives + assistant execution) to prevent context loss in long sessions.
- **Unified Schema**: All data is normalized before analysis, ensuring consistent results regardless of the source.
- **Integrated Insights**: Combines session data with GitHub commits, local git logs, and Obsidian notes.
- **Automated Visualization**: Generates temporal dashboards and interactive canvases in Obsidian.

## Platform Session Locations

| Platform | Session Storage | Access Method | Format |
|----------|----------------|---------------|--------|
| AI Harness (Claude Code) | `~/.claude/projects/<encoded_path>/*.jsonl` | Direct file read | JSONL |
| AI Harness (Hermes) | `~/.hermes/state.db` | SQLite read-only | SQLite |
| AI Harness (Gemini CLI) | `~/.gemini/tmp/<hash>/chats/*.json` | Direct file read | JSON |
| AI Harness (OpenCode) | `~/.local/share/opencode/opencode.db` | SQLite read-only | SQLite |
| Obsidian | `~/Notebook/*.md` | Recursive Markdown scan | Markdown |
| Local Git | `~/Workspace/**/.git` | Recursive git log scan | Git |

## Workflow Script

The primary interface is `scripts/recall_workflow.py` which orchestrates the following pipeline:

1.  **EXTRACTION**: Uses `recall_cli.py` to pull normalized sessions from specified platforms.
2.  **ANALYSIS (Optional)**: Applies contextual chunking and DSPy topic extraction to individual sessions.
3.  **CORRELATION**: Integrates GitHub/Git activity and restic backups into a unified timeline.
4.  **SYNTHESIS**: Generates a narrative summary and identifies the **One Thing** next action.
5.  **VISUALIZATION**: Updates Obsidian dashboards and canvases.

### CLI Usage (`scripts/recall_cli.py`)

```bash
# Extract sessions from all platforms (last 7 days)
PYTHONPATH=. python3 scripts/recall_cli.py extract --days 7

# Extract and analyze topics using DSPy with contextual chunking
PYTHONPATH=. python3 scripts/recall_cli.py extract --days 7 --analyze --model openai/gpt-4o-mini

# Full correlation and synthesis
PYTHONPATH=. python3 scripts/recall_cli.py correlate --days 7 --github-repo owner/repo

# Search across aggregated sessions
PYTHONPATH=. python3 scripts/recall_cli.py search "authentication" --days 30
```

## Contextual Chunking Strategy

To handle long-running sessions that might exceed LLM context windows or contain multiple distinct topics, the system uses a `ContextualChunker`:

1.  **Temporal Splits**: Automatically starts a new chunk if there is a gap of >30 minutes between messages.
2.  **Semantic Integrity**: Ensures tool calls and their results are kept within the same chunk.
3.  **User-Led Boundaries**: Prefers splitting at user messages (which typically introduce new instructions) when character limits (default 8,000) are reached.

## DSPy Signatures

The correlation engine uses structured signatures for synthesis:

```python
class SessionTopicExtractor(dspy.Signature):
    """Extract topics/actions from a session chunk."""
    session_content: str = dspy.InputField()
    topics: List[str] = dspy.OutputField()
    files_touched: List[str] = dspy.OutputField()
    key_actions: List[str] = dspy.OutputField()

class TimelineSynthesizer(dspy.Signature):
    """Synthesize coherent narrative from timeline events."""
    sessions: List[Dict] = dspy.InputField()
    commits: List[Dict] = dspy.InputField()
    narrative: str = dspy.OutputField()
    workstreams: List[str] = dspy.OutputField()

class OneThingGenerator(dspy.Signature):
    """Generate single highest-leverage next action."""
    recent_activity: str = dspy.InputField()
    one_thing: str = dspy.OutputField()
```

## Anti-Hallucination & Evidence-Based Synthesis

- **Evidence Requirement**: A "Workstream" MUST be backed by a Git commit, substantial assistant content (>5 messages), or documented file modifications.
- **Template Isolation**: Never carry over "Active Projects" from previous recalls unless validated by *current* data.
- **Zero Tolerance for Fluff**: Narratives must focus on kinetic energy (work done) rather than potential (untracked folders or empty files).

## Usage Patterns

### Temporal Recall
- `/recall yesterday` (all platforms)
- `/recall last 3 days with github`
- `/recall 2026-04-15`

### Platform/Topic Focused
- `/recall platform:gemini auth work`
- `/recall search "refactoring"`
- `/recall platform:claude code review`

## Performance & Integration

- **Extraction Speed**: ~30 seconds for a full weekly recall.
- **DSPy Synthesis**: 10-15 seconds per analysis.
- **Persistent Memory**: Correlated insights and platform usage patterns are stored in the memory system for cross-session optimization.
