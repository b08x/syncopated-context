#!/usr/bin/env python3
"""Normalized session extraction with DSPy-powered structured outputs.

This module provides:
1. Unified ParsedSession schema across all providers
2. Fixed Gemini path discovery (~/.gemini/tmp/<hash>/chats/*.json)
3. Direct SQLite access for Hermes (no CLI dependency)
4. DSPy signatures for cross-context correlation
5. Multi-source timeline generation (sessions + gh + restic)

Usage:
    python3 normalized_sessions.py extract --days 7 --platforms claude,hermes,gemini
    python3 normalized_sessions.py correlate --days 7 --github-repo owner/repo
    python3 normalized_sessions.py search "authentication work" --days 30
"""

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False

import json
import sqlite3
import glob
import os
import re
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, asdict
from collections import defaultdict


# =============================================================================
# NORMALIZED SCHEMA (matches TypeScript ParsedSession)
# =============================================================================

@dataclass
class SessionUsage:
    """Unified usage metrics across providers."""
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    estimated_cost_usd: float = 0.0
    models_used: List[str] = None
    primary_model: str = "unknown"
    usage_source: str = "session"  # 'session' | 'message'

    def __post_init__(self):
        if self.models_used is None:
            self.models_used = []


@dataclass
class ToolCall:
    """Unified tool call structure."""
    id: str
    name: str
    input: Dict[str, Any]


@dataclass  
class ToolResult:
    """Unified tool result structure."""
    tool_use_id: str
    output: str


@dataclass
class ParsedMessage:
    """Unified message structure."""
    id: str
    session_id: str
    type: Literal['user', 'assistant', 'system']
    content: str
    thinking: Optional[str] = None
    tool_calls: List[ToolCall] = None
    tool_results: List[ToolResult] = None
    usage: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    parent_id: Optional[str] = None

    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []
        if self.tool_results is None:
            self.tool_results = []


@dataclass
class ParsedSession:
    """Unified session schema matching TypeScript implementation."""
    id: str
    project_path: str
    project_name: str
    summary: Optional[str] = None
    generated_title: Optional[str] = None
    title_source: Optional[str] = None  # 'insight' | 'first_message'
    session_character: Optional[str] = None
    started_at: datetime = None
    ended_at: datetime = None
    message_count: int = 0
    user_message_count: int = 0
    assistant_message_count: int = 0
    tool_call_count: int = 0
    compact_count: int = 0
    auto_compact_count: int = 0
    slash_commands: List[str] = None
    git_branch: Optional[str] = None
    claude_version: Optional[str] = None
    source_tool: str = "unknown"
    usage: SessionUsage = None
    messages: List[ParsedMessage] = None

    def __post_init__(self):
        if self.slash_commands is None:
            self.slash_commands = []
        if self.messages is None:
            self.messages = []
        if self.usage is None:
            self.usage = SessionUsage()


# =============================================================================
# DSPY SIGNATURES FOR CORRELATION
# =============================================================================

# Only define DSPy signatures if dspy is available
if DSPY_AVAILABLE:
    class SessionTopicExtractor(dspy.Signature):
        """Extract primary topics and activities from session content.
        
        Analyzes session messages to identify the main areas of work,
        files that were touched, and key actions taken during the session.
        """
        
        session_content: str = dspy.InputField(desc="Combined text content from session messages, truncated to key exchanges")
        topics: List[str] = dspy.OutputField(desc="List of 3-5 main topics/activities in the session, prioritized by time spent")
        files_touched: List[str] = dspy.OutputField(desc="File paths mentioned or modified during the session")
        key_actions: List[str] = dspy.OutputField(desc="Key actions taken (commits, edits, tests run, bugs fixed)")


    class CommitSessionCorrelator(dspy.Signature):
        """Correlate a git commit with the most relevant session(s).
        
        Uses commit message and changed files to find sessions that likely
        relate to this commit, enabling temporal correlation of work.
        """
        
        commit_message: str = dspy.InputField(desc="Git commit message")
        commit_files: List[str] = dspy.InputField(desc="Files changed in commit")
        session_summaries: List[str] = dspy.InputField(desc="List of session summaries to compare against, each with platform and title")
        relevant_session_indices: List[int] = dspy.OutputField(desc="Indices of most relevant sessions (0-based)")
        confidence_scores: List[float] = dspy.OutputField(desc="Confidence scores (0.0-1.0) for each match")


    class TimelineSynthesizer(dspy.Signature):
        """Synthesize a coherent narrative from multiple data sources.
        
        Combines sessions from multiple AI platforms, GitHub commits,
        and file changes into a unified timeline with actionable insights.
        """
        
        sessions: List[Dict] = dspy.InputField(desc="List of session data with platform, summary, and timestamp")
        commits: List[Dict] = dspy.InputField(desc="List of git commits with message and sha")
        file_changes: List[Dict] = dspy.InputField(desc="List of file changes from backup analysis")
        narrative: str = dspy.OutputField(desc="Coherent narrative of activities (2-3 sentences per platform)")
        workstreams: List[str] = dspy.OutputField(desc="Distinct workstreams identified (e.g., ['authentication', 'api', 'testing'])")
        next_actions: List[str] = dspy.OutputField(desc="Suggested next actions, specific and actionable")


    class OneThingGenerator(dspy.Signature):
        """Generate the single highest-leverage next action.
        
        Analyzes recent activity across platforms to determine the one
        action that would provide the most value given current momentum.
        """
        
        recent_activity: str = dspy.InputField(desc="Summary of recent work across platforms (3-5 sentences)")
        workstreams: List[str] = dspy.InputField(desc="Active workstreams identified")
        open_questions: List[str] = dspy.InputField(desc="Unresolved questions or blockers (empty list if none)")
        one_thing: str = dspy.OutputField(desc="Single most important next action (specific, actionable, complete sentence)")
        reasoning: str = dspy.OutputField(desc="Why this action is highest leverage (1-2 sentences)")
    
    # =========================================================================
    # DSPy MODULES (Following Best Practices)
    # =========================================================================
    
    class SessionAnalysisModule(dspy.Module):
        """Analyze sessions to extract topics and actions."""
        
        def __init__(self):
            super().__init__()
            self.extract_topics = dspy.ChainOfThought(SessionTopicExtractor)
        
        def forward(self, session_content: str):
            return self.extract_topics(session_content=session_content)
    
    
    class CorrelationModule(dspy.Module):
        """Multi-stage correlation pipeline."""
        
        def __init__(self):
            super().__init__()
            self.correlate_commits = dspy.Predict(CommitSessionCorrelator)
            self.synthesize = dspy.ChainOfThought(TimelineSynthesizer)
            self.one_thing = dspy.ChainOfThought(OneThingGenerator)
        
        def forward(self, sessions: List[Dict], commits: List[Dict], file_changes: List[Dict]):
            # Stage 1: Synthesize timeline
            timeline_result = self.synthesize(
                sessions=sessions,
                commits=commits,
                file_changes=file_changes
            )
            
            # Stage 2: Generate One Thing
            one_thing_result = self.one_thing(
                recent_activity=timeline_result.narrative,
                workstreams=timeline_result.workstreams,
                open_questions=[]  # Could be extracted from session analysis
            )
            
            return dspy.Prediction(
                narrative=timeline_result.narrative,
                workstreams=timeline_result.workstreams,
                next_actions=timeline_result.next_actions,
                one_thing=one_thing_result.one_thing,
                one_thing_reasoning=one_thing_result.reasoning
            )
    
    # Module instances (initialized when needed)
    def get_dspy_modules():
        """Factory function for DSPy modules with lazy initialization."""
        return {
            'session_analyzer': SessionAnalysisModule(),
            'correlator': CorrelationModule()
        }

else:
    # Placeholder classes when dspy is not available
    SessionTopicExtractor = None
    CommitSessionCorrelator = None
    TimelineSynthesizer = None
    OneThingGenerator = None
    SessionAnalysisModule = None
    CorrelationModule = None
    
    def get_dspy_modules():
        return {}


# =============================================================================
# PROVIDER EXTRACTION CLASSES
# =============================================================================

class GeminiProvider:
    """Extract Gemini CLI sessions from ~/.gemini/tmp/<hash>/chats/*.json"""
    
    def __init__(self):
        self.home_dir = Path.home() / ".gemini"
        self.tmp_dir = self.home_dir / "tmp"
        self.projects_file = self.home_dir / "projects.json"
    
    def discover(self, project_filter: Optional[str] = None) -> List[str]:
        """Discover session files using correct Gemini path structure."""
        if not self.tmp_dir.exists():
            return []
        
        # Load project mappings (hash -> name)
        project_mappings = {}
        if self.projects_file.exists():
            try:
                with open(self.projects_file) as f:
                    data = json.load(f)
                    project_mappings = data.get("projects", {})
            except (json.JSONDecodeError, IOError):
                pass
        
        session_files = []
        
        # Scan tmp/<project_hash>/chats/*.json
        for entry in self.tmp_dir.iterdir():
            if not entry.is_dir():
                continue
            
            chats_dir = entry / "chats"
            if not chats_dir.exists():
                continue
            
            # Check project filter
            project_name = project_mappings.get(entry.name, entry.name)
            if project_filter:
                if project_filter.lower() not in project_name.lower() and \
                   project_filter.lower() not in entry.name.lower():
                    continue
            
            # Collect JSON files
            for json_file in chats_dir.glob("*.json"):
                session_files.append(str(json_file))
        
        return session_files
    
    def parse(self, filepath: str) -> Optional[ParsedSession]:
        """Parse Gemini session JSON into normalized schema."""
        try:
            with open(filepath) as f:
                data = json.load(f)
            
            if not data.get("sessionId") or not data.get("messages"):
                return None
            
            # Resolve project info
            project_dir = Path(filepath).parent.parent
            project_id = project_dir.name
            
            project_path = ""
            project_name = project_id
            
            root_file = project_dir / ".project_root"
            if root_file.exists():
                project_path = root_file.read_text().strip()
                project_name = Path(project_path).name
            
            # Parse messages
            messages = []
            user_count = 0
            assistant_count = 0
            tool_count = 0
            
            for msg in data["messages"]:
                if msg.get("type") == "info":
                    continue
                
                msg_type = self._normalize_type(msg["type"])
                content = self._extract_content(msg)
                
                if msg_type == "user":
                    user_count += 1
                elif msg_type == "assistant":
                    assistant_count += 1
                
                # Extract tool calls
                tool_calls = []
                for tc in msg.get("toolCalls", []):
                    tool_calls.append(ToolCall(
                        id=tc.get("id", ""),
                        name=tc.get("name", ""),
                        input=tc.get("args", {})
                    ))
                    tool_count += 1
                
                messages.append(ParsedMessage(
                    id=msg.get("id", ""),
                    session_id=data["sessionId"],
                    type=msg_type,
                    content=content,
                    thinking=self._extract_thinking(msg),
                    tool_calls=tool_calls,
                    tool_results=self._extract_tool_results(msg),
                    usage=self._extract_usage(msg),
                    timestamp=self._parse_timestamp(msg.get("timestamp"))
                ))
            
            if not messages:
                return None
            
            # Calculate usage
            usage = self._calculate_usage(messages, data)
            
            return ParsedSession(
                id=data["sessionId"],
                project_path=project_path,
                project_name=project_name,
                started_at=self._parse_timestamp(data.get("startTime")),
                ended_at=self._parse_timestamp(data.get("lastUpdated")),
                message_count=len(messages),
                user_message_count=user_count,
                assistant_message_count=assistant_count,
                tool_call_count=tool_count,
                source_tool="gemini-cli",
                usage=usage,
                messages=messages
            )
        
        except (json.JSONDecodeError, IOError, KeyError) as e:
            print(f"  [gemini] Parse error {filepath}: {e}")
            return None
    
    def _normalize_type(self, msg_type: str) -> str:
        """Normalize Gemini message types."""
        mapping = {
            "gemini": "assistant",
            "user": "user",
            "info": "system"
        }
        return mapping.get(msg_type, "system")
    
    def _extract_content(self, msg: Dict) -> str:
        """Extract text content from various formats."""
        content = msg.get("content", "")
        
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        parts.append(block.get("text", ""))
                    elif "text" in block:
                        parts.append(block["text"])
                elif isinstance(block, str):
                    parts.append(block)
            return "\n".join(parts)
        
        return ""
    
    def _extract_thinking(self, msg: Dict) -> Optional[str]:
        """Extract thinking/reasoning content."""
        return msg.get("thinking") or msg.get("reasoning")
    
    def _extract_tool_results(self, msg: Dict) -> List[ToolResult]:
        """Extract tool results."""
        results = []
        for tr in msg.get("toolResults", []):
            results.append(ToolResult(
                tool_use_id=tr.get("toolUseId", ""),
                output=str(tr.get("output", ""))
            ))
        return results
    
    def _extract_usage(self, msg: Dict) -> Optional[Dict]:
        """Extract token usage."""
        tokens = msg.get("tokens", {})
        if tokens:
            return {
                "inputTokens": tokens.get("input", 0),
                "outputTokens": tokens.get("output", 0),
                "model": tokens.get("model", "unknown")
            }
        return None
    
    def _parse_timestamp(self, ts: Any) -> Optional[datetime]:
        """Parse various timestamp formats."""
        if not ts:
            return None
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                pass
        return None
    
    def _calculate_usage(self, messages: List[ParsedMessage], data: Dict) -> SessionUsage:
        """Calculate total usage from messages or session-level data."""
        total_in = sum(
            (m.usage or {}).get("inputTokens", 0) for m in messages
        )
        total_out = sum(
            (m.usage or {}).get("outputTokens", 0) for m in messages
        )
        
        models = list(set(
            (m.usage or {}).get("model") for m in messages if m.usage
        ))
        
        return SessionUsage(
            total_input_tokens=total_in,
            total_output_tokens=total_out,
            models_used=models or ["gemini"],
            primary_model=models[0] if models else "gemini"
        )


class HermesProvider:
    """Extract Hermes Agent sessions from ~/.hermes/state.db (SQLite)."""
    
    def __init__(self):
        self.db_path = Path.home() / ".hermes" / "state.db"
    
    def discover(self, project_filter: Optional[str] = None) -> List[str]:
        """Discover sessions via direct SQLite query."""
        if not self.db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            cursor = conn.execute("SELECT id, title FROM sessions")
            
            # Return virtual paths: <db_path>#<session_id>
            virtual_paths = []
            for row in cursor.fetchall():
                session_id, title = row
                
                # Apply project filter on title
                if project_filter and title:
                    if project_filter.lower() not in title.lower():
                        continue
                
                virtual_paths.append(f"{self.db_path}#{session_id}")
            
            conn.close()
            return virtual_paths
        
        except sqlite3.Error as e:
            print(f"  [hermes] SQLite error: {e}")
            return []
    
    def parse(self, virtual_path: str) -> Optional[ParsedSession]:
        """Parse session from SQLite using virtual path format."""
        if "#" not in virtual_path:
            return None
        
        db_path, session_id = virtual_path.rsplit("#", 1)
        
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            
            # Get session metadata
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE id = ?", (session_id,)
            )
            session_row = cursor.fetchone()
            if not session_row:
                conn.close()
                return None
            
            # Get messages
            cursor = conn.execute(
                """SELECT * FROM messages 
                   WHERE session_id = ? 
                   ORDER BY timestamp ASC""",
                (session_id,)
            )
            message_rows = cursor.fetchall()
            
            # Parse messages
            messages = []
            user_count = 0
            assistant_count = 0
            tool_count = 0
            
            for row in message_rows:
                role = row["role"]
                
                # Handle tool results - attach to previous assistant
                if role == "tool":
                    last_asst = None
                    for m in reversed(messages):
                        if m.type == "assistant":
                            last_asst = m
                            break
                    
                    if last_asst:
                        last_asst.tool_results.append(ToolResult(
                            tool_use_id=row["tool_call_id"] or f"tool-{row['id']}",
                            output=row["content"] or ""
                        ))
                    continue
                
                msg_type = "assistant" if role == "assistant" else "user"
                
                if msg_type == "user":
                    user_count += 1
                else:
                    assistant_count += 1
                
                # Parse tool calls from JSON string
                tool_calls = []
                if row["tool_calls"]:
                    try:
                        parsed = json.loads(row["tool_calls"])
                        for tc in parsed:
                            tool_calls.append(ToolCall(
                                id=tc.get("id", ""),
                                name=tc.get("name") or tc.get("function", {}).get("name", ""),
                                input=tc.get("args") or tc.get("function", {}).get("arguments", {})
                            ))
                            tool_count += 1
                    except json.JSONDecodeError:
                        pass
                
                # Timestamp is in SECONDS, need to multiply by 1000 for ms
                timestamp = datetime.fromtimestamp(
                    row["timestamp"], tz=timezone.utc
                ) if row["timestamp"] else None
                
                messages.append(ParsedMessage(
                    id=f"hermes-{row['id']}",
                    session_id=f"hermes-agent:{session_id}",
                    type=msg_type,
                    content=row["content"] or "",
                    thinking=row["reasoning"],
                    tool_calls=tool_calls,
                    tool_results=[],
                    usage={
                        "outputTokens": row["token_count"] or 0,
                        "model": session_row["model"] or "unknown"
                    } if row["token_count"] else None,
                    timestamp=timestamp
                ))
            
            # Build usage from session-level data
            usage = SessionUsage(
                total_input_tokens=session_row["input_tokens"] or 0,
                total_output_tokens=session_row["output_tokens"] or 0,
                cache_creation_tokens=session_row["cache_write_tokens"] or 0,
                cache_read_tokens=session_row["cache_read_tokens"] or 0,
                estimated_cost_usd=session_row["actual_cost_usd"] or 
                                    session_row["estimated_cost_usd"] or 0,
                models_used=[session_row["model"]] if session_row["model"] else [],
                primary_model=session_row["model"] or "unknown"
            )
            
            started = datetime.fromtimestamp(
                session_row["started_at"], tz=timezone.utc
            ) if session_row["started_at"] else None
            ended = datetime.fromtimestamp(
                session_row["ended_at"], tz=timezone.utc
            ) if session_row["ended_at"] else started
            
            conn.close()
            
            return ParsedSession(
                id=f"hermes-agent:{session_id}",
                project_path="",  # Hermes sessions are global
                project_name=session_row["title"] or "hermes-agent-session",
                generated_title=session_row["title"],
                title_source="insight" if session_row["title"] else None,
                started_at=started,
                ended_at=ended,
                message_count=len(messages),
                user_message_count=user_count,
                assistant_message_count=assistant_count,
                tool_call_count=tool_count,
                source_tool="hermes-agent",
                usage=usage,
                messages=messages
            )
        
        except sqlite3.Error as e:
            print(f"  [hermes] Parse error for {session_id}: {e}")
            return None


class ClaudeCodeProvider:
    """Extract Claude Code sessions from ~/.claude/projects/<encoded_path>/*.jsonl"""
    
    def __init__(self):
        self.projects_dir = Path.home() / ".claude" / "projects"
    
    def discover(self, project_filter: Optional[str] = None) -> List[str]:
        """Discover JSONL session files."""
        if not self.projects_dir.exists():
            return []
        
        session_files = []
        
        for project_dir in self.projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
            
            if project_filter:
                if project_filter.lower() not in project_dir.name.lower():
                    continue
            
            for jsonl_file in project_dir.glob("*.jsonl"):
                session_files.append(str(jsonl_file))
        
        return session_files
    
    def parse(self, filepath: str) -> Optional[ParsedSession]:
        """Parse Claude Code JSONL session."""
        # Implementation similar to extract-sessions.py
        # but returns normalized ParsedSession
        try:
            messages = []
            session_id = Path(filepath).stem
            started_at = None
            
            with open(filepath) as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    
                    if obj.get("sessionId"):
                        session_id = obj["sessionId"]
                    
                    if obj.get("type") == "user":
                        content = self._extract_text(
                            obj.get("message", {}).get("content", "")
                        )
                        if content and len(content) >= 5:
                            messages.append(ParsedMessage(
                                id=f"claude-{len(messages)}",
                                session_id=session_id,
                                type="user",
                                content=self._clean_content(content),
                                timestamp=self._parse_ts(obj.get("timestamp"))
                            ))
                    
                    elif obj.get("type") == "assistant":
                        content_blocks = obj.get("message", {}).get("content", [])
                        text_content = ""
                        tool_calls = []
                        
                        if isinstance(content_blocks, list):
                            for block in content_blocks:
                                if isinstance(block, dict):
                                    if block.get("type") == "text":
                                        text_content = block.get("text", "")
                                    elif block.get("type") == "tool_use":
                                        tool_calls.append(ToolCall(
                                            id=block.get("id", ""),
                                            name=block.get("name", ""),
                                            input=block.get("input", {})
                                        ))
                        
                        messages.append(ParsedMessage(
                            id=f"claude-{len(messages)}",
                            session_id=session_id,
                            type="assistant",
                            content=text_content,
                            tool_calls=tool_calls,
                            timestamp=self._parse_ts(obj.get("timestamp"))
                        ))
                    
                    if not started_at and obj.get("timestamp"):
                        started_at = self._parse_ts(obj["timestamp"])
            
            if not messages:
                return None
            
            user_count = sum(1 for m in messages if m.type == "user")
            asst_count = sum(1 for m in messages if m.type == "assistant")
            tool_count = sum(len(m.tool_calls) for m in messages)
            
            # Extract project path from encoded directory name
            project_dir = Path(filepath).parent.name
            project_path = project_dir.replace("-", "/")
            
            return ParsedSession(
                id=session_id,
                project_path=project_path,
                project_name=Path(project_path).name if project_path else "unknown",
                started_at=started_at,
                ended_at=messages[-1].timestamp if messages else started_at,
                message_count=len(messages),
                user_message_count=user_count,
                assistant_message_count=asst_count,
                tool_call_count=tool_count,
                source_tool="claude-code",
                messages=messages
            )
        
        except (IOError, json.JSONDecodeError) as e:
            print(f"  [claude] Parse error {filepath}: {e}")
            return None
    
    def _extract_text(self, content: Any) -> str:
        """Extract text from various content formats."""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif isinstance(block, str):
                    parts.append(block)
            return "\n".join(parts)
        return ""
    
    def _clean_content(self, text: str) -> str:
        """Remove system tags from content."""
        patterns = [
            r"<system-reminder>.*?</system-reminder>",
            r"<local-command-caveat>.*?</local-command-caveat>",
            r"<local-command-stdout>.*?</local-command-stdout>",
            r"<command-name>.*?</command-name>\s*<command-message>.*?</command-message>",
            r"<task-notification>.*?</task-notification>",
            r"<teammate-message[^>]*>.*?</teammate-message>",
        ]
        for pat in patterns:
            text = re.sub(pat, "", text, flags=re.DOTALL)
        return text.strip()
    
    def _parse_ts(self, ts: Any) -> Optional[datetime]:
        """Parse timestamp."""
        if not ts:
            return None
        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                pass
        return None


class OpenCodeProvider:
    """Extract OpenCode sessions from ~/.local/share/opencode/opencode.db"""
    
    def __init__(self):
        self.db_path = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
    
    def discover(self, project_filter: Optional[str] = None) -> List[str]:
        """Discover sessions via SQLite query."""
        if not self.db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            cursor = conn.execute(
                "SELECT id FROM session ORDER BY time_created DESC"
            )
            
            virtual_paths = [f"{self.db_path}#{row[0]}" for row in cursor.fetchall()]
            conn.close()
            return virtual_paths
        
        except sqlite3.Error:
            return []
    
    def parse(self, virtual_path: str) -> Optional[ParsedSession]:
        """Parse OpenCode session from SQLite."""
        if "#" not in virtual_path:
            return None
        
        db_path, session_id = virtual_path.rsplit("#", 1)
        
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            
            # Get session
            cursor = conn.execute(
                """SELECT id, project_id, slug, title, directory, 
                          time_created, time_updated
                   FROM session WHERE id = ?""",
                (session_id,)
            )
            session_row = cursor.fetchone()
            if not session_row:
                conn.close()
                return None
            
            # Get messages (time_created is in MILLISECONDS)
            cursor = conn.execute(
                """SELECT id, data, time_created 
                   FROM message 
                   WHERE session_id = ?
                   ORDER BY time_created ASC""",
                (session_id,)
            )
            message_rows = cursor.fetchall()
            
            messages = []
            for row in message_rows:
                try:
                    data = json.loads(row["data"])
                    role = data.get("role", "unknown")
                    
                    messages.append(ParsedMessage(
                        id=str(row["id"]),
                        session_id=session_id,
                        type=role if role in ["user", "assistant"] else "system",
                        content=self._extract_content(data),
                        tool_calls=self._extract_tools(data),
                        timestamp=datetime.fromtimestamp(
                            row["time_created"] / 1000, tz=timezone.utc
                        )
                    ))
                except json.JSONDecodeError:
                    continue
            
            conn.close()
            
            started = datetime.fromtimestamp(
                session_row["time_created"] / 1000, tz=timezone.utc
            )
            
            return ParsedSession(
                id=session_id,
                project_path=session_row["directory"] or "",
                project_name=session_row["title"] or session_row["slug"] or "opencode-session",
                started_at=started,
                ended_at=datetime.fromtimestamp(
                    session_row["time_updated"] / 1000, tz=timezone.utc
                ) if session_row["time_updated"] else started,
                message_count=len(messages),
                user_message_count=sum(1 for m in messages if m.type == "user"),
                assistant_message_count=sum(1 for m in messages if m.type == "assistant"),
                tool_call_count=sum(len(m.tool_calls) for m in messages),
                source_tool="opencode",
                messages=messages
            )
        
        except sqlite3.Error as e:
            print(f"  [opencode] Parse error: {e}")
            return None
    
    def _extract_content(self, data: Dict) -> str:
        """Extract content from message data."""
        content = data.get("content", "")
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
            return "\n".join(parts)
        return ""
    
    def _extract_tools(self, data: Dict) -> List[ToolCall]:
        """Extract tool calls from message data."""
        calls = []
        content = data.get("content", [])
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    calls.append(ToolCall(
                        id=block.get("id", ""),
                        name=block.get("name", ""),
                        input=block.get("input", {})
                    ))
        return calls


# =============================================================================
# MULTI-SOURCE CORRELATION
# =============================================================================

class MultiSourceCorrelator:
    """Correlate sessions with git commits, restic backups, and notebook changes."""
    
    def __init__(self):
        self.providers = {
            "gemini": GeminiProvider(),
            "hermes": HermesProvider(),
            "claude": ClaudeCodeProvider(),
            "opencode": OpenCodeProvider()
        }
    
    def extract_all(self, days: int = 7, 
                    platforms: Optional[List[str]] = None) -> Dict[str, List[ParsedSession]]:
        """Extract sessions from all platforms."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        results = {}
        platforms = platforms or list(self.providers.keys())
        
        for platform in platforms:
            if platform not in self.providers:
                continue
            
            provider = self.providers[platform]
            files = provider.discover()
            
            sessions = []
            for filepath in files:
                session = provider.parse(filepath)
                if session and session.started_at and session.started_at >= cutoff:
                    sessions.append(session)
            
            results[platform] = sessions
            print(f"  [{platform}] Extracted {len(sessions)} sessions")
        
        return results
    
    def fetch_github_data(self, repo: str, days: int = 7) -> Dict:
        """Fetch GitHub commits and PRs."""
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        # Check gh CLI
        result = subprocess.run(["gh", "--version"], capture_output=True)
        if result.returncode != 0:
            return {"commits": [], "pull_requests": []}
        
        # Get commits
        commits = []
        try:
            result = subprocess.run([
                "gh", "api", f"repos/{repo}/commits",
                "--method", "GET",
                "--field", f"since={since}Z",
                "--jq", ".[] | {sha: .sha[0:7], message: .commit.message, date: .commit.author.date, author: .commit.author.name}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        try:
                            commits.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        except Exception:
            pass
        
        return {"commits": commits, "pull_requests": []}
    
    def build_timeline(self, sessions: Dict[str, List[ParsedSession]],
                       github_data: Optional[Dict] = None) -> List[Dict]:
        """Build unified timeline from all sources."""
        timeline = []
        
        # Add all sessions
        for platform, platform_sessions in sessions.items():
            for session in platform_sessions:
                timeline.append({
                    "type": "session",
                    "platform": platform,
                    "timestamp": session.started_at,
                    "data": asdict(session),
                    "summary": session.generated_title or f"{platform} session"
                })
        
        # Add GitHub commits
        if github_data:
            for commit in github_data.get("commits", []):
                try:
                    ts = datetime.fromisoformat(commit["date"].replace("Z", "+00:00"))
                except (KeyError, ValueError):
                    ts = datetime.now(timezone.utc)
                
                timeline.append({
                    "type": "commit",
                    "platform": "github",
                    "timestamp": ts,
                    "data": commit,
                    "summary": commit.get("message", "").split("\n")[0][:60]
                })
        
        # Sort by timestamp
        return sorted(timeline, key=lambda x: x.get("timestamp") or datetime.min.replace(tzinfo=timezone.utc))
    
    def configure_dspy(self, model: str = "openai/gpt-4o-mini", api_key: Optional[str] = None):
        """Configure DSPy with specified language model.
        
        Args:
            model: Model identifier (e.g., "openai/gpt-4o-mini", "anthropic/claude-sonnet-4-5-20250929")
            api_key: Optional API key (will use env var if not provided)
        
        Returns:
            True if configuration succeeded, False otherwise
        """
        if not DSPY_AVAILABLE:
            return False
        
        try:
            # Support multiple providers
            if model.startswith("openai/"):
                lm = dspy.LM(model, api_key=api_key)
            elif model.startswith("anthropic/"):
                lm = dspy.LM(model, api_key=api_key)
            elif model.startswith("ollama/"):
                # Local Ollama models
                _, model_name = model.split("/", 1)
                lm = dspy.LM(f"ollama_chat/{model_name}")
            else:
                lm = dspy.LM(model)
            
            dspy.configure(lm=lm)
            return True
        except Exception as e:
            print(f"  [dspy] Configuration error: {e}")
            return False
    
    def correlate_with_dspy(self, timeline: List[Dict], model: str = "openai/gpt-4o-mini") -> Dict:
        """Use DSPy to generate correlated narrative and next actions.
        
        Multi-stage pipeline:
        1. Configure LM with specified model
        2. Synthesize timeline from sessions + commits + file changes
        3. Generate One Thing recommendation
        
        Args:
            timeline: List of timeline events (sessions, commits, file changes)
            model: DSPy-compatible model identifier
        
        Returns:
            Dict with narrative, workstreams, next_actions, one_thing
        """
        if not DSPY_AVAILABLE:
            return self._heuristic_correlation(timeline)
        
        # Configure DSPy
        if not self.configure_dspy(model):
            return self._heuristic_correlation(timeline)
        
        # Prepare input data (limit to prevent context overflow)
        sessions = [
            {
                "platform": t["platform"],
                "summary": t.get("summary", "Untitled session"),
                "timestamp": t.get("timestamp", "").isoformat() if hasattr(t.get("timestamp"), "isoformat") else str(t.get("timestamp", ""))
            }
            for t in timeline if t["type"] == "session"
        ][:10]
        
        commits = [
            {
                "message": t["data"].get("message", "").split("\n")[0][:100],
                "sha": t["data"].get("sha", "")[:8]
            }
            for t in timeline if t["type"] == "commit"
        ][:10]
        
        file_changes = []  # TODO: Integrate restic backup analysis
        
        # Get DSPy modules
        modules = get_dspy_modules()
        correlator = modules.get('correlator')
        
        if not correlator:
            return self._heuristic_correlation(timeline)
        
        try:
            # Run correlation pipeline
            result = correlator(
                sessions=sessions,
                commits=commits,
                file_changes=file_changes
            )
            
            return {
                "narrative": result.narrative,
                "workstreams": result.workstreams,
                "next_actions": result.next_actions,
                "one_thing": result.one_thing,
                "one_thing_reasoning": result.one_thing_reasoning
            }
        except Exception as e:
            print(f"  [dspy] Pipeline error: {e}")
            return self._heuristic_correlation(timeline)
    
    def _heuristic_correlation(self, timeline: List[Dict]) -> Dict:
        """Fallback heuristic-based correlation."""
        sessions = [t for t in timeline if t["type"] == "session"]
        platforms = set(s["platform"] for s in sessions)
        
        # Extract topics from summaries
        topics = defaultdict(int)
        for s in sessions:
            for word in s["summary"].lower().split():
                if len(word) > 4 and word.isalpha():
                    topics[word] += 1
        
        top_topics = sorted(topics.items(), key=lambda x: -x[1])[:5]
        
        return {
            "narrative": f"Activity across {len(platforms)} platforms: {', '.join(platforms)}",
            "workstreams": [t[0] for t in top_topics[:3]],
            "next_actions": [f"Continue {top_topics[0][0]} work" if top_topics else "Review recent sessions"]
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Normalized session extraction with DSPy correlation")
    sub = parser.add_subparsers(dest="command", required=True)
    
    # Extract command
    p_extract = sub.add_parser("extract", help="Extract sessions from platforms")
    p_extract.add_argument("--days", type=int, default=7, help="Days to extract")
    p_extract.add_argument("--platforms", help="Comma-separated platforms (gemini,hermes,claude,opencode)")
    p_extract.add_argument("--output", help="Output JSON file")
    
    # Correlate command
    p_correlate = sub.add_parser("correlate", help="Correlate sessions with GitHub and generate timeline")
    p_correlate.add_argument("--days", type=int, default=7)
    p_correlate.add_argument("--github-repo", help="GitHub repo (owner/name)")
    p_correlate.add_argument("--model", default="openai/gpt-4o-mini",
                              help="DSPy model (default: openai/gpt-4o-mini)")
    p_correlate.add_argument("--output", help="Output JSON file")
    
    # Search command
    p_search = sub.add_parser("search", help="Search sessions by topic")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--days", type=int, default=30)
    p_search.add_argument("--platforms", help="Comma-separated platforms")
    
    args = parser.parse_args()
    
    correlator = MultiSourceCorrelator()
    
    def serialize_message(msg):
        """Convert message to JSON-serializable dict."""
        if hasattr(msg, '__dataclass_fields__'):
            data = asdict(msg)
        else:
            data = dict(msg) if isinstance(msg, dict) else {'content': str(msg)}
        
        if data.get('timestamp'):
            data['timestamp'] = data['timestamp'].isoformat() if hasattr(data['timestamp'], 'isoformat') else str(data['timestamp'])
        
        # Handle tool_calls and tool_results
        if data.get('tool_calls'):
            data['tool_calls'] = [asdict(tc) if hasattr(tc, '__dataclass_fields__') else tc for tc in data['tool_calls']]
        if data.get('tool_results'):
            data['tool_results'] = [asdict(tr) if hasattr(tr, '__dataclass_fields__') else tr for tr in data['tool_results']]
        
        return data
    
    def serialize_session(session):
        """Convert session to JSON-serializable dict."""
        data = asdict(session)
        # Handle datetime fields
        for field in ['started_at', 'ended_at']:
            if data.get(field) and hasattr(data[field], 'isoformat'):
                data[field] = data[field].isoformat()
        # Handle nested usage (already a dict after asdict)
        if data.get('usage') and hasattr(data['usage'], '__dataclass_fields__'):
            data['usage'] = asdict(data['usage'])
        # Handle nested messages
        data['messages'] = [serialize_message(m) for m in (data.get('messages') or [])]
        return data
    
    if args.command == "extract":
        platforms = args.platforms.split(",") if args.platforms else None
        sessions = correlator.extract_all(args.days, platforms)
        
        # Convert to serializable format
        output = {}
        for platform, platform_sessions in sessions.items():
            output[platform] = [serialize_session(s) for s in platform_sessions]
        
        if args.output:
            with open(args.output, "w") as f:
                json.dump(output, f, indent=2)
            print(f"\n✓ Saved to {args.output}")
        else:
            print(json.dumps(output, indent=2))
    
    elif args.command == "correlate":
        sessions = correlator.extract_all(args.days)
        
        github_data = None
        if args.github_repo:
            print(f"\n Fetching GitHub data for {args.github_repo}...")
            github_data = correlator.fetch_github_data(args.github_repo, args.days)
            print(f"   Found {len(github_data['commits'])} commits")
        
        timeline = correlator.build_timeline(sessions, github_data)
        
        print(f"\n correlating {len(timeline)} events...")
        result = correlator.correlate_with_dspy(timeline, model=args.model)
        
        print(f"\n{'='*60}")
        print(result["narrative"])
        print(f"\n Workstreams: {', '.join(result['workstreams'])}")
        print(f"\n Next Actions:")
        for action in result["next_actions"]:
            print(f"   • {action}")
        
        if result.get("one_thing"):
            print(f"\n ONE THING: {result['one_thing']}")
            if result.get("one_thing_reasoning"):
                print(f" Reasoning: {result['one_thing_reasoning']}")
        
        if args.output:
            # Recursively serialize any datetime objects
            def serialize_value(v):
                if hasattr(v, 'isoformat'):
                    return v.isoformat()
                elif isinstance(v, dict):
                    return {k2: serialize_value(v2) for k2, v2 in v.items()}
                elif isinstance(v, list):
                    return [serialize_value(item) for item in v]
                else:
                    return v
            
            def serialize_timeline_event(event):
                return {k: serialize_value(v) for k, v in event.items()}
            
            with open(args.output, "w") as f:
                json.dump({
                    "timeline": [serialize_timeline_event(t) for t in timeline],
                    "correlation": result
                }, f, indent=2)
            print(f"\n✓ Saved to {args.output}")
    
    elif args.command == "search":
        platforms = args.platforms.split(",") if args.platforms else None
        sessions = correlator.extract_all(args.days, platforms)
        
        # Simple keyword search
        results = []
        query_lower = args.query.lower()
        
        for platform, platform_sessions in sessions.items():
            for session in platform_sessions:
                # Search in title and message content
                title_match = session.generated_title and query_lower in session.generated_title.lower()
                content_match = any(
                    query_lower in m.content.lower() 
                    for m in session.messages
                )
                
                if title_match or content_match:
                    results.append({
                        "platform": platform,
                        "session_id": session.id,
                        "title": session.generated_title or "Untitled",
                        "started_at": session.started_at.isoformat() if session.started_at else None,
                        "message_count": session.message_count
                    })
        
        print(f"\n Found {len(results)} matching sessions")
        for r in results[:20]:
            print(f"  [{r['platform']}] {r['title'][:50]} ({r['message_count']} msgs)")


if __name__ == "__main__":
    main()
