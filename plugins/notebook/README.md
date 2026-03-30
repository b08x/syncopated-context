# notebook

Multi-platform AI session recall and analysis suite for Claude Code. Comprehensive session aggregation across Claude Code, Hermes, Gemini CLI, and OpenCode with GitHub commit correlation, restic backup diff analysis, and intelligent synthesis.

[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](.claude-plugin/plugin.json)
[![Category](https://img.shields.io/badge/category-productivity-blue.svg)](.claude-plugin/plugin.json)

---

## Features

- **Multi-platform session extraction** — aggregates AI interactions from Claude Code, Hermes, Gemini CLI, and OpenCode with unified query interface
- **Temporal correlation** — aligns session timestamps with external events for comprehensive work reconstruction
- **GitHub integration** — correlates commit history, PR activity, and code changes with session timelines using `gh cli`
- **Backup diff analysis** — analyzes restic incremental backups to show file evolution synchronized with session activity
- **Cross-platform synthesis** — identifies work patterns and connections across different AI tools and platforms
- **One Thing generation** — synthesizes single highest-leverage next action using momentum detection and blocker identification
- **Interactive visualization** — generates temporal graphs showing session-file relationships and work clustering
- **NotebookLM integration** — processes documents and artifacts with advanced query capabilities

---

## Installation

<details>
<summary>Claude Code — Plugin Marketplace (Recommended)</summary>

```bash
claude plugin add syncopated-context/notebook
```

</details>

<details>
<summary>Manual install from source</summary>

```bash
git clone https://github.com/b08x/syncopated-context
cd syncopated-context
claude plugin add ./plugins/notebook
```

</details>

<details>
<summary>Prerequisites</summary>

**Required for multi-platform recall:**
- Python 3.8+
- `hermes` CLI (for Hermes sessions)
- `gh` CLI (for GitHub integration)
- `restic` (for backup diff analysis)

**Optional:**
- Obsidian (for knowledge base workflows)
- NotebookLM access (for document processing)

</details>

---

## Usage

### Basic Session Recall

```bash
# Temporal recall across all platforms
recall yesterday
recall last week
recall 2025-03-25

# Topic-based recall
recall authentication work
recall debugging session
recall schema design
```

### Multi-Platform Recall

```bash
# All platforms for time period
recall yesterday across platforms
recall last week across platforms

# Platform-specific recall
recall platform:hermes auth work
recall platform:gemini debugging session
recall platform:opencode code review
recall platform:claude schema design
```

### Integrated Analysis

```bash
# GitHub commit correlation
recall --github owner/repo commits yesterday
recall --github myrepo authentication work

# Backup diff analysis
recall --backup ~/Workspace schema changes
recall --backup ~/Projects file evolution

# Full integration
recall --github myrepo --backup ~/Workspace authentication refactor
recall platform:claude platform:hermes --github myrepo debugging
```

### Graph Visualization

```bash
# Interactive session graphs
recall graph yesterday
recall graph last week
recall graph this week --min-files 5
```

---

## Platform Support

### AI Session Sources

| Platform | Storage Location | Export Command | Format |
|----------|------------------|---------------|--------|
| **Claude Code** | `~/.claude/projects/*/` | Native JSONL parsing | JSONL |
| **Hermes** | SQLite store | `hermes sessions export --format jsonl` | JSONL |
| **Gemini CLI** | `~/.config/gemini/sessions/` | JSON file parsing | JSON |
| **OpenCode** | `~/.config/opencode/logs/` | Log file parsing | Structured logs |

### External Integrations

- **GitHub** — `gh api repos/owner/repo/commits` with timestamp correlation
- **Restic** — `restic diff snapshot1 snapshot2` for incremental file changes
- **NotebookLM** — document import and query processing

---

## Architecture

```
notebook/
├── skills/
│   ├── recall/
│   │   ├── SKILL.md                      — multi-platform recall skill
│   │   ├── scripts/
│   │   │   ├── multi-platform-extract.py — unified platform extraction
│   │   │   ├── extract-sessions.py       — Claude Code JSONL parser
│   │   │   ├── recall-day.py             — temporal session retrieval
│   │   │   └── session-graph.py          — NetworkX visualization
│   │   └── workflows/
│   │       ├── recall.md                 — query routing and classification
│   │       └── multi-platform-recall.md  — correlation process
│   ├── notebooklm/                       — document processing workflows
│   └── query/                            — Obsidian CLI and ck-search integration
└── .claude-plugin/
    └── plugin.json                       — plugin metadata
```

### Correlation Engine

The multi-platform extraction script coordinates:

1. **Platform-specific extraction** — session retrieval from each AI platform
2. **Temporal correlation** — alignment by timestamp with configurable windows
3. **GitHub integration** — commit and PR correlation with session activity
4. **Backup analysis** — file change detection from restic incremental diffs
5. **Cross-platform synthesis** — pattern detection and momentum analysis
6. **One Thing generation** — highest-leverage action synthesis

### Query Classification

The recall workflow automatically detects:

- **Multi-platform queries** — "across platforms", "all AI tools", contains `platform:`, `github:`, `backup:`
- **Temporal queries** — "yesterday", "last week", date expressions
- **Topic queries** — subject keywords and search terms
- **Graph queries** — "graph" prefix for visualization requests

---

## Output Formats

### Session Summary Table

```
Platform        | Sessions | Time Range              | Key Topics
----------------|----------|-------------------------|------------------
Claude Code     | 5        | 2025-03-25 to 03-30   | auth, recall
Hermes          | 2        | 2025-03-27 to 03-28   | debugging, API
Gemini CLI      | 1        | 2025-03-29             | code review
```

### Timeline Correlation

```
2025-03-25 09:30 [Claude] Started auth refactor discussion
2025-03-25 09:45 [GitHub] Commit: "WIP: authentication middleware"
2025-03-25 10:15 [Restic] Modified: src/auth.py, tests/auth_test.py

2025-03-27 14:20 [Hermes] Debugging session timeout issues
2025-03-27 14:35 [GitHub] PR created: "Fix session timeout handling"
2025-03-27 15:00 [Restic] Modified: lib/session_manager.py
```

### One Thing Synthesis

```
🎯 ONE THING: Complete the session timeout fix from your Hermes debugging
session by merging PR #23 and updating the auth middleware tests based on
your Claude Code session insights.

💡 Reasoning: Highest momentum topic spanning 3 platforms with recent GitHub
activity and unblocked path to completion.
```

---

## Configuration

The recall skill supports customization via arguments:

### Date Expressions
- Relative: `yesterday`, `today`, `last week`, `this week`
- Absolute: `2025-03-25`, `2025-03-20 to 2025-03-25`
- Relative with offset: `3 days ago`, `last 7 days`

### Platform Filtering
- Single platform: `platform:hermes`, `platform:claude`
- Multiple platforms: `platform:hermes platform:gemini`
- All platforms: default behavior when no platform specified

### Integration Options
- GitHub: `--github owner/repo`
- Backup analysis: `--backup ~/path/to/workspace`
- Combined: `--github myrepo --backup ~/Workspace`

### Graph Options
- File threshold: `--min-files 5` (sessions touching 5+ files)
- Message threshold: `--min-msgs 3` (sessions with 3+ messages)
- Project scope: `--all-projects` (scan beyond current directory)

---

## Troubleshooting

### Platform-Specific Issues

**Hermes sessions not found:**
```bash
# Check Hermes CLI availability
hermes sessions list

# Export sessions manually
hermes sessions export --format jsonl --days 7
```

**Gemini CLI sessions missing:**
```bash
# Check session directory
ls ~/.config/gemini/sessions/

# Verify JSON format
cat ~/.config/gemini/sessions/latest.json
```

**OpenCode logs inaccessible:**
```bash
# Check log directory permissions
ls -la ~/.config/opencode/logs/

# Verify structured format
head -20 ~/.config/opencode/logs/latest.log
```

### Integration Issues

**GitHub CLI not authenticated:**
```bash
gh auth status
gh auth login
```

**Restic repository not configured:**
```bash
restic snapshots
export RESTIC_REPOSITORY=/path/to/repo
```

---

## Roadmap

- **Real-time session streaming** — live correlation as sessions progress
- **Semantic search** — vector-based session content search beyond keyword matching
- **Team collaboration** — shared session pools and cross-team correlation
- **Plugin ecosystem** — extensible platform support for additional AI tools
- **Advanced visualization** — 3D temporal graphs and workflow pattern recognition

---

## Contributing

Issues and pull requests welcome. Multi-platform testing requires access to all supported AI platforms.

## License

[MIT](../../LICENSE) — Robert Pannick