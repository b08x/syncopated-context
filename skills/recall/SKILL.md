---
name: recall
description: Use when user asks to recall work across multiple AI platforms (Claude Code, Gemini CLI, OpenCode, Hermes), correlate with GitHub activity, or analyze file changes from backups. Handles temporal queries, topic searches, and cross-platform session aggregation. Triggers on "recall", "what did we work on", "session history across platforms", "multi-platform recall", "GitHub commits", "backup diffs", "restic changes".
argument-hint: [yesterday|today|last week|TOPIC|platform:PLATFORM_NAME|github:REPO|backup:PATH]
allowed-tools: Bash(python3:*), Bash(hermes:*), Bash(gemini:*), Bash(opencode:*), Bash(gh:*), Bash(restic:*), Bash(sqlite3:*)
---

# Multi-Platform Recall Skill

Comprehensive session recall across Claude Code, Gemini CLI, OpenCode, and Hermes with GitHub activity correlation and backup diff analysis. Every recall ends with the **One Thing** - a concrete, highest-leverage next action synthesized from cross-platform results.

## Architecture Overview

This skill uses a **normalized extraction layer** that unifies session data from all providers into a common `ParsedSession` schema, enabling:

- **Provider-agnostic queries**: Same analysis works across all platforms
- **Schema consistency**: Unified field names, timestamp formats, usage metrics
- **Cross-platform correlation**: Sessions from different tools can be compared
- **DSPy-powered synthesis**: Structured LLM calls for narrative generation

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Claude Code    │     │   Gemini CLI     │     │    Hermes       │
│  JSONL files    │     │   JSON files     │     │   SQLite DB    │
└────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
         │                       │                         │
         └───────────────────────┼─────────────────────────┘
                                 ▼
                    ┌───────────────────────┐
                    │  Normalization Layer  │
                    │  (ParsedSession)      │
                    └───────────┬───────────┘
                                ▼
                    ┌───────────────────────┐
                    │   DSPy Correlation    │
                    │   Timeline Synthesis   │
                    └───────────┬───────────┘
                                ▼
                    ┌───────────────────────┐
                    │   GitHub + Restic      │
                    │   Multi-Context        │
                    └───────────────────────┘
```

## What It Does

- **Multi-platform session aggregation**: Extracts and correlates sessions from all major AI platforms
- **Normalized schema**: All providers output identical `ParsedSession` structure
- **GitHub integration**: Pulls commit history, PR activity for contextual insights
- **Backup correlation**: Analyzes restic incremental diffs for file evolution
- **Temporal correlation**: Aligns session timestamps with commits and file changes
- **DSPy synthesis**: Uses structured signatures for narrative generation
- **One Thing generation**: Synthesizes single most impactful next action

## Platform Session Locations

| Platform | Session Storage | Access Method | Format |
|----------|----------------|---------------|--------|
| Claude Code | `~/.claude/projects/<encoded_path>/*.jsonl` | Direct file read | JSONL |
| Hermes | `~/.hermes/state.db` | SQLite read-only | SQLite |
| Gemini CLI | `~/.gemini/tmp/<hash>/chats/*.json` | Direct file read | JSON |
| OpenCode | `~/.local/share/opencode/opencode.db` | SQLite read-only | SQLite |

**Critical Path Fixes:**

- **Gemini**: Use `~/.gemini/tmp/<hash>/chats/*.json` (NOT `antigravity/conversations`)
- **Hermes**: Direct SQLite access (NOT CLI export dependency)
- **All providers**: Output unified `ParsedSession` schema

## Workflow Script

The primary interface is `scripts/recall_workflow.py` which orchestrates:

```
STAGE 1: EXTRACTION     → Multi-provider normalized extraction
STAGE 2: CORRELATION    → GitHub + restic integration, timeline build
STAGE 3: SEARCH         → Optional topic search across combined data
STAGE 4: ONE THING      → DSPy synthesis of highest-leverage action
```

### Basic Usage

```bash
# Standard recall - last 7 days, all platforms
python3 scripts/recall_workflow.py

# Extended timeframe with GitHub integration
python3 scripts/recall_workflow.py --days 14 --github-repo owner/repo

# Topic search across platforms
python3 scripts/recall_workflow.py --search "authentication work" --days 30

# Specific platforms only
python3 scripts/recall_workflow.py --platforms claude,hermes --days 7
```

### Output Structure

```
/tmp/recall-output/
├── sessions_20260402_093000.json      # Extracted normalized sessions
├── correlation_20260402_093000.json   # Timeline + synthesis results
└── search_results.json                 # (if --search used)
```

## Normalized Session Schema

All providers output this unified structure:

```python
@dataclass
class ParsedSession:
    id: str                              # Unique session identifier
    project_path: str                    # Project directory path
    project_name: str                    # Project name
    summary: Optional[str]               # LLM-generated summary (if available)
    generated_title: Optional[str]       # Extracted or generated title
    title_source: Optional[str]         # 'insight' | 'first_message'
    session_character: Optional[str]     # Agent personality (if applicable)
    started_at: datetime                 # Session start timestamp
    ended_at: datetime                   # Session end timestamp
    message_count: int                   # Total messages
    user_message_count: int              # User messages only
    assistant_message_count: int        # Assistant messages only
    tool_call_count: int                 # Tool invocations
    compact_count: int                   # Context compaction events
    auto_compact_count: int              # Automatic compactions
    slash_commands: List[str]            # Slash commands used
    git_branch: Optional[str]            # Active git branch
    claude_version: Optional[str]         # Claude version (Claude Code only)
    source_tool: str                     # Provider name
    usage: SessionUsage                  # Token usage metrics
    messages: List[ParsedMessage]        # Normalized messages
```

## DSPy Signatures

The correlation engine uses structured signatures for synthesis:

```python
class SessionTopicExtractor(dspy.Signature):
    """Extract primary topics and activities from session content."""
    session_content: str = dspy.InputField()
    topics: List[str] = dspy.OutputField()
    files_touched: List[str] = dspy.OutputField()
    key_actions: List[str] = dspy.OutputField()

class TimelineSynthesizer(dspy.Signature):
    """Synthesize coherent narrative from multiple data sources."""
    sessions: List[Dict] = dspy.InputField()
    commits: List[Dict] = dspy.InputField()
    file_changes: List[Dict] = dspy.InputField()
    narrative: str = dspy.OutputField()
    workstreams: List[str] = dspy.OutputField()
    next_actions: List[str] = dspy.OutputField()

class OneThingGenerator(dspy.Signature):
    """Generate single highest-leverage next action."""
    recent_activity: str = dspy.InputField()
    open_questions: List[str] = dspy.InputField()
    one_thing: str = dspy.OutputField()
    reasoning: str = dspy.OutputField()
```

**Fallback**: If DSPy unavailable, heuristic-based synthesis is used.

### DSPy Configuration

Environment variables control the LLM used for DSPy-powered synthesis:

| Variable | Default | Description |
|----------|---------|-------------|
| `RECALL_DSPY_PROVIDER` | `openrouter` | LLM provider (openrouter, openai, anthropic, ollama) |
| `RECALL_DSPY_MODEL` | `openai/gpt-4.1-nano` | Model identifier for synthesis |

```bash
# OpenRouter (default) - model includes provider prefix
export RECALL_DSPY_PROVIDER=openrouter
export RECALL_DSPY_MODEL=openai/gpt-4.1-nano  # Format: <provider>/<model>

# Direct OpenAI
export RECALL_DSPY_PROVIDER=openai
export RECALL_DSPY_MODEL=gpt-4o-mini

# Anthropic
export RECALL_DSPY_PROVIDER=anthropic
export RECALL_DSPY_MODEL=claude-sonnet-4-5-20250929

# Local Ollama
export RECALL_DSPY_PROVIDER=ollama
export RECALL_DSPY_MODEL=llama3.2
```

DSPy LM configuration follows this pattern:
```python
lm = dspy.LM(
    "openrouter/openai/gpt-4.1-nano",  # Format: openrouter/<model-id>
    api_key="...",
    base_url="https://openrouter.ai/api/v1"
)
```

## Implementation Details

### Stage 1: Multi-Provider Extraction

```bash
# Direct script access for extraction-only
python3 scripts/normalized_sessions.py extract --days 7 --platforms all

# Output: JSON with normalized sessions per provider
{
  "claude": [ParsedSession, ...],
  "hermes": [ParsedSession, ...],
  "gemini": [ParsedSession, ...],
  "opencode": [ParsedSession, ...]
}
```

**Provider-specific fixes applied:**

- **Gemini**: Correct path `~/.gemini/tmp/<hash>/chats/*.json` + `.project_root` resolution
- **Hermes**: Direct SQLite with proper timestamp handling (seconds, not milliseconds)
- **Claude**: Existing JSONL parsing preserved
- **OpenCode**: SQLite query with millisecond timestamp conversion

### Stage 2: Correlation

```bash
# Correlation with GitHub integration
python3 scripts/normalized_sessions.py correlate --days 7 --github-repo owner/repo

# Output: Timeline + synthesis
{
  "timeline": [
    {"type": "session", "platform": "hermes", "timestamp": "...", "summary": "..."},
    {"type": "commit", "platform": "github", "timestamp": "...", "data": {...}}
  ],
  "correlation": {
    "narrative": "Activity across 3 platforms...",
    "workstreams": ["authentication", "api design", "testing"],
    "next_actions": ["Continue auth work", "Review API changes"]
  }
}
```

### Stage 3: Topic Search

```bash
# Search across all normalized sessions
python3 scripts/normalized_sessions.py search "authentication" --days 30

# Results ranked by relevance
Found 12 matching sessions
  [hermes] OAuth implementation session (23 msgs)
  [claude] JWT token refresh work (45 msgs)
  [gemini] Auth middleware debugging (18 msgs)
```

## Common Baseline Failure Patterns

| Failure Pattern | Agent Rationalization | Reality |
|-----------------|----------------------|---------|
| "I can only search current directory" | "Assumes user is in wrong repo" | Need to access platform-specific storage locations |
| "Cannot access other AI tools" | "No capability to read session files" | Each platform has documented storage and export methods |
| "GitHub requires authentication" | "Assumes complex API integration needed" | `gh cli` handles auth and provides simple commands |
| "Generic next steps instead of actual data" | "Better to give advice than admit limitations" | Users need actual session content, not suggestions |

**Red Flags - Use This Skill:**
- "I can only search the current directory"
- "I don't have access to your other AI tools"
- "Let me suggest some next steps instead"
- "You should manually check your sessions"

## Usage Patterns

### Temporal Recall
```
/recall yesterday                    # All platforms, yesterday
/recall last week across platforms   # Multi-platform aggregation
/recall 2025-03-25 with github      # Include GitHub activity
/recall this week with backups      # Include restic diffs
```

### Platform-Specific
```
/recall platform:hermes last 3 days # Hermes only
/recall platform:gemini auth work   # Gemini sessions on "auth"
/recall platform:claude code review # Claude Code sessions on "code review"
```

### Integrated Analysis
```
/recall github:myrepo auth commits   # GitHub commits + related sessions
/recall backup:~/Workspace changes  # File changes + session correlation
/recall cross-platform debugging    # All sources for "debugging" topic
```

## Anti-Hallucination & Evidence-Based Synthesis

To prevent "Strategic Hype" or parroting of template content, the following rules apply to all synthesis operations:

- **Evidence Requirement**: A "Workstream" or "Initiative" MUST be backed by at least one of:
    - A Git commit within the requested timeframe.
    - At least 5 assistant messages of substantial content in a normalized session.
    - Explicit file modifications (not just creation) documented in `file_changes`.
- **Template Isolation**: Never carry over "Active Projects" or "Next Actions" from a previous dashboard or template unless they are validated by *current* session data.
- **The "?? " Rule**: Items found in `git status` as untracked (??) are "Environmental Noise" and should be listed as "Potential Future Work" or "Untracked Artifacts," NOT as active initiatives.
- **Zero Tolerance for Fluff**: If the last 3 days were just "plumbing," the narrative must state "Infrastructure stabilization" rather than inventing "Strategic Pivot to [Folder Name]."

## Performance Notes

- **Session extraction**: ~30 seconds for 7 days across all platforms
- **Normalization overhead**: <5 seconds for schema alignment
- **DSPy synthesis**: 10-15 seconds for narrative generation
- **GitHub API**: Rate limited to 5000 requests/hour
- **SQLite access**: Read-only, no locking conflicts
- **Fallback heuristics**: Instant, deterministic results

## Integration with Persistent Memory

When configured with the memory system:
- Cross-platform patterns stored as user memories
- Failed correlation attempts stored as feedback memories
- Project-specific session insights stored as project memories
- Platform usage patterns tracked for optimization
