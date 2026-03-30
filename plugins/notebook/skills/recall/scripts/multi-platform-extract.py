#!/usr/bin/env python3
"""Multi-platform session extraction for recall skill.

Extracts sessions from Claude Code, Hermes, Gemini CLI, and OpenCode,
with optional GitHub and restic backup integration.

Usage:
    python3 multi-platform-extract.py [options] [query]

Examples:
    python3 multi-platform-extract.py yesterday
    python3 multi-platform-extract.py --platform hermes auth work
    python3 multi-platform-extract.py --github myrepo --backup ~/Workspace last week
"""

import argparse
import json
import glob
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any


class MultiPlatformExtractor:
    """Extract sessions from multiple AI platforms with correlation."""

    def __init__(self):
        self.platforms = ['claude', 'hermes', 'gemini', 'opencode']

    def extract_sessions(self, platforms: List[str], date_range: Dict,
                        topic: Optional[str] = None) -> Dict[str, List[Dict]]:
        """Extract sessions from specified platforms."""
        results = {}

        for platform in platforms:
            try:
                sessions = self._extract_platform_sessions(platform, date_range, topic)
                results[platform] = sessions
                print(f"✓ {platform}: {len(sessions)} sessions")
            except Exception as e:
                print(f"✗ {platform}: {str(e)}")
                results[platform] = []

        return results

    def _extract_platform_sessions(self, platform: str, date_range: Dict,
                                 topic: Optional[str]) -> List[Dict]:
        """Extract sessions from specific platform."""
        extractors = {
            'claude': self._extract_claude_sessions,
            'hermes': self._extract_hermes_sessions,
            'gemini': self._extract_gemini_sessions,
            'opencode': self._extract_opencode_sessions
        }

        if platform not in extractors:
            raise ValueError(f"Unsupported platform: {platform}")

        sessions = extractors[platform](date_range)

        if topic:
            sessions = self._filter_by_topic(sessions, topic)

        return sessions

    def _extract_claude_sessions(self, date_range: Dict) -> List[Dict]:
        """Extract Claude Code sessions using existing script."""
        script_path = Path(__file__).parent / "extract-sessions.py"
        days = (date_range['end'] - date_range['start']).days + 1

        cmd = f"python3 {script_path} --days {days}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Claude extraction failed: {result.stderr}")

        # Parse existing extraction output (would need to modify extract-sessions.py to output JSON)
        sessions = []
        # For now, use glob to find recent JSONL files
        claude_dir = os.path.expanduser("~/.claude/projects")
        if os.path.exists(claude_dir):
            for project_dir in os.listdir(claude_dir):
                project_path = os.path.join(claude_dir, project_dir)
                if os.path.isdir(project_path):
                    for jsonl_file in glob.glob(f"{project_path}/*.jsonl"):
                        sessions.extend(self._parse_claude_jsonl(jsonl_file, date_range))

        return sessions

    def _extract_hermes_sessions(self, date_range: Dict) -> List[Dict]:
        """Extract Hermes sessions via CLI export."""
        days = (date_range['end'] - date_range['start']).days + 1

        # Try hermes sessions export
        cmd = f"hermes sessions export --format jsonl --days {days}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            # Fallback: try hermes sessions list with JSON output
            cmd = "hermes sessions list --json"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"Hermes extraction failed: {result.stderr}")

        sessions = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    session = json.loads(line)
                    session['platform'] = 'hermes'
                    sessions.append(session)
                except json.JSONDecodeError:
                    continue

        return self._filter_by_date_range(sessions, date_range)

    def _extract_gemini_sessions(self, date_range: Dict) -> List[Dict]:
        """Extract Gemini CLI sessions from config directory."""
        session_dir = os.path.expanduser("~/.config/gemini/sessions/")
        sessions = []

        if not os.path.exists(session_dir):
            return sessions

        for file_path in glob.glob(f"{session_dir}/*.json"):
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc)
            if self._is_in_date_range(file_time, date_range):
                try:
                    with open(file_path, 'r') as f:
                        session = json.load(f)
                        session['platform'] = 'gemini'
                        session['file_path'] = file_path
                        session['timestamp'] = file_time.isoformat()
                        sessions.append(session)
                except (json.JSONDecodeError, IOError):
                    continue

        return sessions

    def _extract_opencode_sessions(self, date_range: Dict) -> List[Dict]:
        """Extract OpenCode sessions from log files."""
        log_dir = os.path.expanduser("~/.config/opencode/logs/")
        sessions = []

        if not os.path.exists(log_dir):
            return sessions

        # Find recent log files
        for file_path in glob.glob(f"{log_dir}/*.log"):
            if self._is_file_in_date_range(file_path, date_range):
                sessions.extend(self._parse_opencode_logs(file_path))

        return sessions

    def _parse_claude_jsonl(self, file_path: str, date_range: Dict) -> List[Dict]:
        """Parse Claude Code JSONL session file."""
        sessions = []
        current_session = None

        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        obj = json.loads(line)

                        # New session marker
                        if obj.get('type') == 'session_start' or obj.get('sessionId'):
                            if current_session:
                                sessions.append(current_session)

                            current_session = {
                                'platform': 'claude',
                                'session_id': obj.get('sessionId', Path(file_path).stem),
                                'messages': [],
                                'file_path': file_path,
                                'timestamp': obj.get('timestamp')
                            }

                        # Message
                        elif obj.get('role') in ['user', 'assistant']:
                            if current_session:
                                current_session['messages'].append(obj)
                                if not current_session.get('timestamp'):
                                    current_session['timestamp'] = obj.get('timestamp')

                    except json.JSONDecodeError:
                        continue

                if current_session:
                    sessions.append(current_session)

        except IOError:
            pass

        return [s for s in sessions if self._session_in_date_range(s, date_range)]

    def _parse_opencode_logs(self, file_path: str) -> List[Dict]:
        """Parse OpenCode log files for session data."""
        sessions = []

        try:
            with open(file_path, 'r') as f:
                content = f.read()

                # Look for conversation patterns (this is a guess at OpenCode format)
                session_blocks = re.split(r'\n\n\[SESSION START\]|\n\n---', content)

                for i, block in enumerate(session_blocks):
                    if not block.strip():
                        continue

                    # Extract timestamp if present
                    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', block)
                    timestamp = timestamp_match.group(1) if timestamp_match else None

                    # Extract messages (USER/ASSISTANT pattern)
                    messages = []
                    for line in block.split('\n'):
                        if line.strip().startswith('USER:'):
                            messages.append({'role': 'user', 'content': line[5:].strip()})
                        elif line.strip().startswith('ASSISTANT:'):
                            messages.append({'role': 'assistant', 'content': line[10:].strip()})

                    if messages:
                        sessions.append({
                            'platform': 'opencode',
                            'session_id': f"{Path(file_path).stem}_{i}",
                            'messages': messages,
                            'file_path': file_path,
                            'timestamp': timestamp or datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                        })

        except IOError:
            pass

        return sessions

    def fetch_github_data(self, repo: str, date_range: Dict) -> Dict:
        """Fetch GitHub commits and PR activity."""
        since = date_range['start'].isoformat() + 'Z'
        until = date_range['end'].isoformat() + 'Z'

        # Check if gh cli is available
        result = subprocess.run(['gh', '--version'], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError("GitHub CLI (gh) not available")

        # Get commits
        commits_cmd = [
            'gh', 'api', f'repos/{repo}/commits',
            '--method', 'GET',
            '--field', f'since={since}',
            '--field', f'until={until}',
            '--jq', '.[] | {sha: .sha, message: .commit.message, date: .commit.author.date, author: .commit.author.name}'
        ]

        commits_result = subprocess.run(commits_cmd, capture_output=True, text=True)
        commits = []
        if commits_result.returncode == 0:
            for line in commits_result.stdout.strip().split('\n'):
                if line:
                    try:
                        commits.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        # Get PR activity
        prs_cmd = [
            'gh', 'pr', 'list', '--repo', repo, '--state', 'all', '--limit', '50',
            '--json', 'number,title,createdAt,updatedAt,author,state'
        ]

        prs_result = subprocess.run(prs_cmd, capture_output=True, text=True)
        prs = []
        if prs_result.returncode == 0:
            try:
                all_prs = json.loads(prs_result.stdout)
                # Filter PRs by date range
                for pr in all_prs:
                    created = datetime.fromisoformat(pr['createdAt'].replace('Z', '+00:00'))
                    updated = datetime.fromisoformat(pr['updatedAt'].replace('Z', '+00:00'))
                    if (created >= date_range['start'] or updated >= date_range['start']):
                        prs.append(pr)
            except json.JSONDecodeError:
                pass

        return {'commits': commits, 'pull_requests': prs}

    def analyze_backup_diffs(self, backup_path: str, date_range: Dict) -> List[Dict]:
        """Analyze restic backup diffs for file changes."""
        # Check if restic is available
        result = subprocess.run(['restic', 'version'], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError("Restic not available")

        # Get snapshots in date range
        snapshots_cmd = ['restic', 'snapshots', '--json']
        snapshots_result = subprocess.run(snapshots_cmd, capture_output=True, text=True)

        if snapshots_result.returncode != 0:
            raise RuntimeError(f"Failed to get snapshots: {snapshots_result.stderr}")

        snapshots = json.loads(snapshots_result.stdout)

        # Filter snapshots by date range
        relevant_snapshots = []
        for snapshot in snapshots:
            snapshot_time = datetime.fromisoformat(snapshot['time'].replace('Z', '+00:00'))
            if date_range['start'] <= snapshot_time <= date_range['end']:
                relevant_snapshots.append(snapshot)

        # Sort by time (newest first)
        relevant_snapshots.sort(key=lambda x: x['time'], reverse=True)

        # Get diffs between consecutive snapshots
        diffs = []
        for i in range(len(relevant_snapshots) - 1):
            current = relevant_snapshots[i]['id']
            previous = relevant_snapshots[i + 1]['id']

            diff_cmd = ['restic', 'diff', previous, current, '--json']
            diff_result = subprocess.run(diff_cmd, capture_output=True, text=True)

            if diff_result.returncode == 0:
                try:
                    diff_data = json.loads(diff_result.stdout)
                    diffs.append({
                        'snapshot_id': current,
                        'timestamp': relevant_snapshots[i]['time'],
                        'changes': diff_data
                    })
                except json.JSONDecodeError:
                    continue

        return self._filter_backup_changes(diffs, backup_path)

    def _filter_backup_changes(self, diffs: List[Dict], backup_path: str) -> List[Dict]:
        """Filter backup changes to only include relevant paths."""
        if not backup_path:
            return diffs

        filtered_diffs = []
        for diff in diffs:
            relevant_changes = []
            for change in diff.get('changes', []):
                if change.get('path', '').startswith(backup_path):
                    relevant_changes.append(change)

            if relevant_changes:
                filtered_diff = diff.copy()
                filtered_diff['changes'] = relevant_changes
                filtered_diffs.append(filtered_diff)

        return filtered_diffs

    def correlate_timeline(self, sessions: Dict[str, List[Dict]],
                          github_data: Dict, backup_diffs: List[Dict]) -> List[Dict]:
        """Correlate sessions with commits and file changes."""
        timeline = []

        # Flatten all sessions
        all_sessions = []
        for platform, platform_sessions in sessions.items():
            for session in platform_sessions:
                session['platform'] = platform
                all_sessions.append(session)

        for session in all_sessions:
            session_time = self._parse_session_timestamp(session)
            if not session_time:
                continue

            # Find commits within 30 minutes of session
            nearby_commits = []
            for commit in github_data.get('commits', []):
                commit_time = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
                time_diff = abs((session_time - commit_time).total_seconds())
                if time_diff < 1800:  # 30 minutes
                    nearby_commits.append(commit)

            # Find file changes that might relate to session
            related_changes = []
            session_files = self._extract_files_mentioned_in_session(session)
            for diff in backup_diffs:
                diff_time = datetime.fromisoformat(diff['timestamp'].replace('Z', '+00:00'))
                time_diff = abs((session_time - diff_time).total_seconds())

                # Check if session mentions files that changed
                changed_files = [f.get('path', '') for f in diff.get('changes', [])
                               if f.get('type') in ['added', 'modified']]
                file_overlap = any(f in self._get_session_content(session) for f in changed_files if f)

                if time_diff < 3600 and file_overlap:  # 1 hour window + file relevance
                    related_changes.append(diff)

            timeline.append({
                'session': session,
                'platform': session['platform'],
                'timestamp': session_time,
                'commits': nearby_commits,
                'file_changes': related_changes
            })

        return sorted(timeline, key=lambda x: x['timestamp'])

    def generate_one_thing(self, timeline: List[Dict]) -> Dict:
        """Generate the single highest-leverage next action."""
        if not timeline:
            return {'action': 'No recent activity found', 'reasoning': 'No sessions or activity detected'}

        # Simple heuristic-based synthesis (would be more sophisticated in practice)
        recent_sessions = timeline[-5:]  # Last 5 sessions
        platforms_used = set(s['platform'] for s in recent_sessions)

        # Find most mentioned topics
        topics = {}
        for entry in recent_sessions:
            content = self._get_session_content(entry['session'])
            words = content.lower().split()
            for word in words:
                if len(word) > 4 and word.isalpha():
                    topics[word] = topics.get(word, 0) + 1

        top_topic = max(topics.items(), key=lambda x: x[1])[0] if topics else "development"

        # Check for recent commits
        has_recent_commits = any(len(e['commits']) > 0 for e in recent_sessions)

        action = f"Continue {top_topic} work across {len(platforms_used)} platforms"
        reasoning = f"Most active topic with activity across {', '.join(platforms_used)}"

        if has_recent_commits:
            action += " and review recent commits"
            reasoning += " with recent Git activity"

        return {
            'topic': top_topic,
            'action': action,
            'reasoning': reasoning,
            'platforms': list(platforms_used)
        }

    # Helper methods
    def _filter_by_topic(self, sessions: List[Dict], topic: str) -> List[Dict]:
        """Filter sessions by topic/keyword."""
        filtered = []
        for session in sessions:
            content = self._get_session_content(session)
            if topic.lower() in content.lower():
                filtered.append(session)
        return filtered

    def _filter_by_date_range(self, sessions: List[Dict], date_range: Dict) -> List[Dict]:
        """Filter sessions by date range."""
        filtered = []
        for session in sessions:
            session_time = self._parse_session_timestamp(session)
            if session_time and self._is_in_date_range(session_time, date_range):
                filtered.append(session)
        return filtered

    def _session_in_date_range(self, session: Dict, date_range: Dict) -> bool:
        """Check if session falls within date range."""
        session_time = self._parse_session_timestamp(session)
        return session_time and self._is_in_date_range(session_time, date_range)

    def _is_in_date_range(self, timestamp: datetime, date_range: Dict) -> bool:
        """Check if timestamp falls within date range."""
        return date_range['start'] <= timestamp <= date_range['end']

    def _is_file_in_date_range(self, file_path: str, date_range: Dict) -> bool:
        """Check if file modification time falls within date range."""
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc)
        return self._is_in_date_range(file_time, date_range)

    def _parse_session_timestamp(self, session: Dict) -> Optional[datetime]:
        """Parse session timestamp."""
        timestamp_str = session.get('timestamp')
        if not timestamp_str:
            return None

        try:
            # Handle various timestamp formats
            if isinstance(timestamp_str, str):
                if 'Z' in timestamp_str:
                    return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    return datetime.fromisoformat(timestamp_str)
        except (ValueError, AttributeError):
            pass

        return None

    def _get_session_content(self, session: Dict) -> str:
        """Extract text content from session."""
        content = []
        messages = session.get('messages', [])

        for msg in messages:
            if isinstance(msg, dict):
                content.append(msg.get('content', ''))
            elif isinstance(msg, str):
                content.append(msg)

        return ' '.join(content)

    def _extract_files_mentioned_in_session(self, session: Dict) -> List[str]:
        """Extract file paths mentioned in session."""
        content = self._get_session_content(session)

        # Simple regex to find file paths
        file_patterns = [
            r'\b[\w/.-]+\.(py|js|ts|rb|md|json|yaml|yml|txt|log)\b',
            r'\b[\w.-]+/[\w/.-]+\b',
        ]

        files = []
        for pattern in file_patterns:
            files.extend(re.findall(pattern, content))

        return list(set(files))


def parse_date_range(date_arg: str) -> Dict[str, datetime]:
    """Parse date argument into start/end datetime range."""
    now = datetime.now(timezone.utc)

    if date_arg == 'yesterday':
        start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(hour=23, minute=59, second=59)
    elif date_arg == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif date_arg == 'last week':
        start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif date_arg == 'this week':
        days_since_monday = now.weekday()
        start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif re.match(r'\d{4}-\d{2}-\d{2}', date_arg):
        date = datetime.strptime(date_arg, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = date.replace(hour=23, minute=59, second=59)
    else:
        # Default to last 7 days
        start = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = now

    return {'start': start, 'end': end}


def main():
    parser = argparse.ArgumentParser(description='Multi-platform session recall')
    parser.add_argument('query', nargs='*', help='Date range or topic query')
    parser.add_argument('--platform', action='append', help='Specific platform(s) to query')
    parser.add_argument('--github', help='GitHub repo for commit correlation (owner/repo)')
    parser.add_argument('--backup', help='Backup path for restic diff analysis')
    parser.add_argument('--output', help='Output file (default: stdout)')

    args = parser.parse_args()

    extractor = MultiPlatformExtractor()

    # Parse query arguments
    platforms = args.platform if args.platform else extractor.platforms
    date_range = None
    topic = None

    for arg in args.query:
        if arg in ['yesterday', 'today', 'last week', 'this week'] or re.match(r'\d{4}-\d{2}-\d{2}', arg):
            date_range = parse_date_range(arg)
        else:
            topic = ' '.join(args.query)
            break

    if not date_range:
        date_range = parse_date_range('last week')  # Default

    print(f"🔍 Recalling from {len(platforms)} platforms: {', '.join(platforms)}")
    print(f"📅 Date range: {date_range['start'].strftime('%Y-%m-%d')} to {date_range['end'].strftime('%Y-%m-%d')}")
    if topic:
        print(f"🔎 Topic filter: {topic}")

    # Extract sessions
    sessions = extractor.extract_sessions(platforms, date_range, topic)
    total_sessions = sum(len(s) for s in sessions.values())
    print(f"\n📋 Total sessions found: {total_sessions}")

    # GitHub integration
    github_data = {}
    if args.github:
        try:
            print(f"🐙 Fetching GitHub data for {args.github}...")
            github_data = extractor.fetch_github_data(args.github, date_range)
            print(f"✓ GitHub: {len(github_data.get('commits', []))} commits, {len(github_data.get('pull_requests', []))} PRs")
        except Exception as e:
            print(f"✗ GitHub integration failed: {e}")

    # Backup analysis
    backup_diffs = []
    if args.backup:
        try:
            print(f"💾 Analyzing backup diffs for {args.backup}...")
            backup_diffs = extractor.analyze_backup_diffs(args.backup, date_range)
            print(f"✓ Restic: {len(backup_diffs)} backup diffs")
        except Exception as e:
            print(f"✗ Backup analysis failed: {e}")

    # Correlate timeline
    print("\n🔗 Correlating timeline...")
    timeline = extractor.correlate_timeline(sessions, github_data, backup_diffs)

    # Generate One Thing
    one_thing = extractor.generate_one_thing(timeline)

    # Output results
    results = {
        'summary': {
            'platforms': {platform: len(sessions.get(platform, [])) for platform in platforms},
            'total_sessions': total_sessions,
            'date_range': {
                'start': date_range['start'].isoformat(),
                'end': date_range['end'].isoformat()
            },
            'topic': topic,
            'github_data': {
                'commits': len(github_data.get('commits', [])),
                'pull_requests': len(github_data.get('pull_requests', []))
            },
            'backup_diffs': len(backup_diffs)
        },
        'sessions': sessions,
        'github_data': github_data,
        'backup_diffs': backup_diffs,
        'timeline': timeline,
        'one_thing': one_thing
    }

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📝 Results written to {args.output}")
    else:
        print(f"\n🎯 ONE THING: {one_thing['action']}")
        print(f"💡 Reasoning: {one_thing['reasoning']}")


if __name__ == '__main__':
    main()