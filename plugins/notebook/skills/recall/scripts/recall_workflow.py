#!/usr/bin/env python3
"""Multi-context session recall workflow.

Orchestrates extraction, correlation, and analysis across all session providers
with optional GitHub and restic backup integration.

Usage:
    python3 scripts/recall_workflow.py
    python3 scripts/recall_workflow.py --days 14 --github-repo owner/repo
"""

import subprocess
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta


# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_DAYS = 7
DEFAULT_PLATFORMS = ["claude", "hermes", "gemini", "opencode"]
OUTPUT_DIR = Path("/tmp/recall-output")


# =============================================================================
# WORKFLOW STAGES
# =============================================================================

def stage_extract(days: int, platforms: list, output_path: Path) -> bool:
    """Extract sessions from all providers into normalized schema.
    
    This stage:
    - Discovers session files from each provider's storage location
    - Parses provider-specific formats (JSON, JSONL, SQLite)
    - Normalizes to unified ParsedSession schema
    - Outputs schema-consistent JSON for downstream processing
    
    Args:
        days: Number of days to look back
        platforms: List of provider names to extract from
        output_path: Path to save extracted sessions JSON
        
    Returns:
        True if extraction succeeded, False otherwise
    """
    print(f"\n{'='*60}")
    print("STAGE 1: MULTI-PROVIDER EXTRACTION")
    print(f"{'='*60}")
    print(f"  Time window: Last {days} days")
    print(f"  Providers: {', '.join(platforms)}")
    print(f"  Output: {output_path}")
    print()
    
    cmd = [
        "python3",
        "scripts/normalized_sessions.py",
        "extract",
        "--days", str(days),
        "--platforms", ",".join(platforms),
        "--output", str(output_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print extraction summary
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.startswith('[') or line.startswith('✓'):
                    print(f"  {line}")
        
        if result.returncode != 0:
            print(f"  ✗ Extraction failed: {result.stderr}")
            return False
            
        # Load and summarize extracted sessions
        if output_path.exists():
            with open(output_path) as f:
                data = json.load(f)
            total = sum(len(sessions) for sessions in data.values())
            print(f"\n  Total sessions extracted: {total}")
            for platform, sessions in data.items():
                if sessions:
                    print(f"    • {platform}: {len(sessions)} sessions")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Extraction error: {e}")
        return False


def stage_correlate(days: int, github_repo: str, output_path: Path, model: str = "openai/gpt-4o-mini") -> dict:
    """Correlate sessions with GitHub commits and generate timeline.
    
    This stage:
    - Fetches GitHub commits for the specified repo (if provided)
    - Builds unified timeline from sessions + commits + backup diffs
    - Uses DSPy to synthesize narrative, workstreams, and next actions
    - Falls back to heuristics if DSPy unavailable
    
    Args:
        days: Number of days to analyze
        github_repo: GitHub repo in owner/name format (or None)
        output_path: Path to save correlation results JSON
        model: DSPy-compatible model identifier
    
    Returns:
        Correlation results dict with narrative, workstreams, next_actions, one_thing
    """
    print(f"\n{'='*60}")
    print("STAGE 2: MULTI-SOURCE CORRELATION")
    print(f"{'='*60}")
    print(f"  Time window: Last {days} days")
    if github_repo:
        print(f"  GitHub repo: {github_repo}")
    print(f"  Model: {model}")
    print(f"  Output: {output_path}")
    print()
    
    cmd = [
        "python3",
        "scripts/normalized_sessions.py",
        "correlate",
        "--days", str(days),
        "--model", model,
        "--output", str(output_path)
    ]
    
    if github_repo:
        cmd.extend(["--github-repo", github_repo])
    
    # Run correlation (output is written to --output path by normalized_sessions.py)
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  ✗ Correlation failed: {result.stderr}")
        return {}
    
    # Print progress messages from subprocess
    for line in result.stdout.strip().split('\n'):
        if line.startswith('[') or line.startswith('Fetching') or line.startswith('correlating'):
            print(f"  {line}")
    
    # Load results from file
    if not output_path.exists():
        print(f"  ✗ Output file not created: {output_path}")
        return {}
    
    with open(output_path) as f:
        results = json.load(f)
    
    # Display One Thing prominently
    correlation = results.get('correlation', {})
    if correlation.get('one_thing'):
        print(f"\n  ONE THING: {correlation['one_thing']}")
        if correlation.get('one_thing_reasoning'):
            print(f"  Reasoning: {correlation['one_thing_reasoning']}")
    
    return correlation


def stage_search(query: str, days: int, platforms: list) -> list:
    """Search sessions by topic keywords.
    
    This stage:
    - Extracts sessions from all providers
    - Performs keyword matching on title and content
    - Returns ranked list of matching sessions
    
    Args:
        query: Search query string
        days: Number of days to search
        platforms: List of providers to search
        
    Returns:
        List of matching session metadata dicts
    """
    print(f"\n{'='*60}")
    print("STAGE 3: TOPIC SEARCH")
    print(f"{'='*60}")
    print(f"  Query: '{query}'")
    print(f"  Time window: Last {days} days")
    print(f"  Providers: {', '.join(platforms)}")
    print()
    
    cmd = [
        "python3",
        "scripts/normalized_sessions.py",
        "search",
        query,
        "--days", str(days)
    ]
    
    if platforms:
        cmd.extend(["--platforms", ",".join(platforms)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"  ✗ Search failed: {result.stderr}")
            return []
        
        # Print results
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if line.startswith('Found') or line.startswith('['):
                print(f"  {line}")
        
        # Try to parse results from output
        results = []
        for line in lines:
            if line.strip().startswith('['):
                # Parse session match format: [platform] title (N msgs)
                parts = line.split(']', 1)
                if len(parts) == 2:
                    platform = parts[0].strip('[').strip()
                    rest = parts[1].strip()
                    results.append({
                        'platform': platform,
                        'match': rest
                    })
        
        return results
        
    except Exception as e:
        print(f"  ✗ Search error: {e}")
        return []


def stage_one_thing(correlation: dict) -> str:
    """Generate the single highest-leverage next action.
    
    This stage:
    - Analyzes correlation results for workstreams and blockers
    - Uses DSPy OneThingGenerator signature for synthesis
    - Falls back to heuristic selection if DSPy unavailable
    
    Args:
        correlation: Correlation results from stage_correlate
        
    Returns:
        Single recommended action string
    """
    print(f"\n{'='*60}")
    print("STAGE 4: ONE THING GENERATION")
    print(f"{'='*60}")
    print()
    
    # Use correlation results to determine one thing
    if not correlation:
        print("  ⚠ No correlation data available")
        return "Review recent sessions to identify next steps"
    
    workstreams = correlation.get('workstreams', [])
    next_actions = correlation.get('next_actions', [])
    
    if next_actions:
        one_thing = next_actions[0]
    elif workstreams:
        one_thing = f"Continue {workstreams[0]} work"
    else:
        one_thing = "Review and synthesize recent activity"
    
    print(f"  Recommended action:\n")
    print(f"    → {one_thing}")
    print()
    
    return one_thing


# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def run_workflow(days: int = DEFAULT_DAYS, 
                 platforms: list = None,
                 github_repo: str = None,
                 search_query: str = None,
                 model: str = "openai/gpt-4o-mini") -> dict:
    """Execute the complete recall workflow.
    
    Pipeline:
    1. Extract sessions from all providers (normalized schema)
    2. Correlate with GitHub commits (if repo provided)
    3. Search for specific topics (if query provided)
    4. Generate single recommended action
    
    Args:
        days: Number of days to analyze
        platforms: List of providers to extract from
        github_repo: GitHub repo in owner/name format
        search_query: Optional topic search query
        model: DSPy-compatible model identifier
        
    Returns:
        Dict with extracted_sessions, correlation, search_results, one_thing
    """
    platforms = platforms or DEFAULT_PLATFORMS
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extract_path = OUTPUT_DIR / f"sessions_{timestamp}.json"
    correlate_path = OUTPUT_DIR / f"correlation_{timestamp}.json"
    
    print(f"\n{'#'*60}")
    print(f"# RECALL WORKFLOW - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'#'*60}")
    
    results = {
        'extracted_sessions': {},
        'correlation': {},
        'search_results': [],
        'one_thing': None
    }
    
    # Stage 1: Extract
    if not stage_extract(days, platforms, extract_path):
        print("\n  ✗ Workflow halted: extraction failed")
        return results
    
    if extract_path.exists():
        with open(extract_path) as f:
            results['extracted_sessions'] = json.load(f)
    
    # Stage 2: Correlate
    correlation = stage_correlate(days, github_repo, correlate_path, model)
    results['correlation'] = correlation
    
    if correlate_path.exists():
        with open(correlate_path) as f:
            results['correlation'] = json.load(f).get('correlation', {})
    
    # Stage 3: Search (optional)
    if search_query:
        results['search_results'] = stage_search(search_query, days, platforms)
    
    # Stage 4: One Thing (use from correlation if available)
    if results['correlation'].get('one_thing'):
        results['one_thing'] = results['correlation']['one_thing']
        print(f"\n{'='*60}")
        print("STAGE 4: ONE THING GENERATION")
        print(f"{'='*60}")
        print(f"\n  Recommended action:\n")
        print(f"    → {results['one_thing']}")
        if results['correlation'].get('one_thing_reasoning'):
            print(f"\n  Reasoning: {results['correlation']['one_thing_reasoning']}")
        print()
    else:
        results['one_thing'] = stage_one_thing(results['correlation'])
    
    # Summary
    print(f"\n{'='*60}")
    print("WORKFLOW COMPLETE")
    print(f"{'='*60}")
    total_sessions = sum(len(s) for s in results['extracted_sessions'].values())
    print(f"  Sessions extracted: {total_sessions}")
    print(f"  Workstreams identified: {len(results['correlation'].get('workstreams', []))}")
    print(f"  Search matches: {len(results['search_results'])}")
    print(f"\n  ONE THING: {results['one_thing']}")
    print(f"\n  Output directory: {OUTPUT_DIR}")
    print(f"{'='*60}\n")
    
    return results


def main():
    global OUTPUT_DIR  # Allow override from command line
    
    parser = argparse.ArgumentParser(
        description="Multi-context session recall workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS,
                        help=f"Days to analyze (default: {DEFAULT_DAYS})")
    
    parser.add_argument("--platforms", 
                        help="Comma-separated providers (default: all)")
    
    parser.add_argument("--github-repo",
                        help="GitHub repo in owner/name format")
    
    parser.add_argument("--search",
                        help="Optional topic search query")
    
    parser.add_argument("--model", default="openai/gpt-4o-mini",
                        help="DSPy model (default: openai/gpt-4o-mini)")
    
    parser.add_argument("--output", type=Path, default=None,
                        help=f"Output directory (default: {OUTPUT_DIR})")
    
    args = parser.parse_args()
    
    platforms = args.platforms.split(",") if args.platforms else None
    
    if args.output:
        OUTPUT_DIR = args.output
    
    run_workflow(
        days=args.days,
        platforms=platforms,
        github_repo=args.github_repo,
        search_query=args.search,
        model=args.model
    )


if __name__ == "__main__":
    main()
