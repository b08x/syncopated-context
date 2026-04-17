#!/usr/bin/env python3
"""
Sync repository skills, commands, agents, references, and tasks into local
AI harness folders.

The sync plan is manifest-driven so new harnesses or source roots can be added
without duplicating copy logic.
"""

from __future__ import annotations

import argparse
import fnmatch
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent.resolve()


class SyncError(ValueError):
    """Raised when sync configuration or inputs are invalid."""


@dataclass(frozen=True)
class SourceRule:
    source: Path
    mode: str
    namespace: str | None = None
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    strip_suffix: str | None = None
    require_file: str | None = None


@dataclass(frozen=True)
class SyncRule:
    profile: str
    name: str
    destination: Path
    sources: tuple[SourceRule, ...]


@dataclass(frozen=True)
class CopyPlanItem:
    source: Path
    destination: Path


def default_rules(home_dir: Path) -> list[SyncRule]:
    repo_skills = SourceRule(REPO_ROOT / "skills", mode="child_dirs", require_file="SKILL.md")
    bashsmithing_skills = SourceRule(
        REPO_ROOT / "plugins" / "bashsmithing" / "skills",
        mode="child_dirs",
        namespace="bashsmithing",
        require_file="SKILL.md",
    )
    rubysmithing_skills = SourceRule(
        REPO_ROOT / "plugins" / "rubysmithing" / "skills",
        mode="child_dirs",
        namespace="rubysmithing",
        require_file="SKILL.md",
    )

    root_commands = SourceRule(
        REPO_ROOT / "commands",
        mode="tree_files",
        include=("*.md",),
        exclude=("gemini/*", "README.md"),
    )
    rubysmithing_commands = SourceRule(
        REPO_ROOT / "plugins" / "rubysmithing" / "commands",
        mode="tree_files",
        namespace="rubysmithing",
        include=("*.md",),
        exclude=("README.md",),
    )

    root_agents = SourceRule(
        REPO_ROOT / "agents",
        mode="tree_files",
        include=("*.md",),
    )
    rubysmithing_agents = SourceRule(
        REPO_ROOT / "plugins" / "rubysmithing" / "agents",
        mode="tree_files",
        namespace="rubysmithing",
        include=("*.md",),
    )

    root_references = SourceRule(
        REPO_ROOT / "references",
        mode="tree_files",
        include=("*",),
    )
    rubysmithing_references = SourceRule(
        REPO_ROOT / "plugins" / "rubysmithing" / "references",
        mode="tree_files",
        namespace="rubysmithing",
        include=("*",),
    )

    root_tasks = SourceRule(
        REPO_ROOT / "tasks",
        mode="tree_files",
        include=("*",),
    )
    rubysmithing_tasks = SourceRule(
        REPO_ROOT / "plugins" / "rubysmithing" / "tasks",
        mode="tree_files",
        namespace="rubysmithing",
        include=("*",),
    )

    crush_skills = SourceRule(
        REPO_ROOT / ".ck" / "skills",
        mode="tree_files",
        include=("*",),
        strip_suffix=".ck",
    )
    crush_commands = SourceRule(
        REPO_ROOT / ".ck" / "commands",
        mode="tree_files",
        include=("*",),
        strip_suffix=".ck",
    )

    return [
        SyncRule(
            profile="gemini",
            name="gemini-skills",
            destination=home_dir / ".gemini" / "skills",
            sources=(repo_skills, bashsmithing_skills, rubysmithing_skills),
        ),
        SyncRule(
            profile="gemini",
            name="gemini-commands",
            destination=home_dir / ".gemini" / "commands",
            sources=(
                SourceRule(
                    REPO_ROOT / "commands" / "gemini",
                    mode="tree_files",
                    include=("*.toml",),
                ),
            ),
        ),
        SyncRule(
            profile="claude",
            name="claude-agents",
            destination=home_dir / ".claude" / "agents",
            sources=(root_agents, rubysmithing_agents),
        ),
        SyncRule(
            profile="claude",
            name="claude-skills",
            destination=home_dir / ".claude" / "skills",
            sources=(repo_skills, bashsmithing_skills, rubysmithing_skills),
        ),
        SyncRule(
            profile="claude",
            name="claude-commands",
            destination=home_dir / ".claude" / "commands",
            sources=(root_commands, rubysmithing_commands),
        ),
        SyncRule(
            profile="codex",
            name="codex-skills",
            destination=home_dir / ".codex" / "skills",
            sources=(repo_skills, bashsmithing_skills, rubysmithing_skills),
        ),
        SyncRule(
            profile="codex",
            name="codex-commands",
            destination=home_dir / ".codex" / "commands",
            sources=(root_commands, rubysmithing_commands),
        ),
        SyncRule(
            profile="opencode",
            name="opencode-agent",
            destination=home_dir / ".config" / "opencode" / "agent",
            sources=(root_agents, rubysmithing_agents),
        ),
        SyncRule(
            profile="opencode",
            name="opencode-command",
            destination=home_dir / ".config" / "opencode" / "command",
            sources=(root_commands, rubysmithing_commands),
        ),
        SyncRule(
            profile="opencode",
            name="opencode-skills",
            destination=home_dir / ".config" / "opencode" / "skills",
            sources=(repo_skills, bashsmithing_skills, rubysmithing_skills),
        ),
        SyncRule(
            profile="opencode",
            name="opencode-references",
            destination=home_dir / ".config" / "opencode" / "references",
            sources=(root_references, rubysmithing_references),
        ),
        SyncRule(
            profile="opencode",
            name="opencode-tasks",
            destination=home_dir / ".config" / "opencode" / "tasks",
            sources=(root_tasks, rubysmithing_tasks),
        ),
        SyncRule(
            profile="crush",
            name="crush-skills",
            destination=home_dir / ".config" / "crush" / "skills",
            sources=(crush_skills,),
        ),
        SyncRule(
            profile="crush",
            name="crush-commands",
            destination=home_dir / ".config" / "crush" / "commands",
            sources=(crush_commands,),
        ),
    ]


class SyncPlanner:
    def __init__(self, rules: Iterable[SyncRule]):
        self.rules = list(rules)

    def select_rules(self, profiles: set[str], rule_names: set[str]) -> list[SyncRule]:
        selected: list[SyncRule] = []
        for rule in self.rules:
            if profiles and rule.profile not in profiles:
                continue
            if rule_names and rule.name not in rule_names:
                continue
            selected.append(rule)

        if not selected:
            raise SyncError("No sync rules matched the requested filters.")

        return selected

    def build_plan(self, rule: SyncRule) -> list[CopyPlanItem]:
        plan: list[CopyPlanItem] = []
        seen_destinations: set[Path] = set()

        for source_rule in rule.sources:
            for item in self._expand_source_rule(source_rule, rule.destination):
                if item.destination in seen_destinations:
                    raise SyncError(f"Destination collision detected: {item.destination}")
                seen_destinations.add(item.destination)
                plan.append(item)

        return plan

    def _expand_source_rule(
        self,
        source_rule: SourceRule,
        destination_root: Path,
    ) -> Iterable[CopyPlanItem]:
        source_root = source_rule.source.resolve()
        if not source_root.exists():
            return []

        destination_base = destination_root
        if source_rule.namespace:
            destination_base = destination_root / source_rule.namespace

        if source_rule.mode == "child_dirs":
            return self._expand_child_dirs(source_rule, source_root, destination_base)
        if source_rule.mode == "tree_files":
            return self._expand_tree_files(source_rule, source_root, destination_base)

        raise SyncError(f"Unsupported source rule mode: {source_rule.mode}")

    def _expand_child_dirs(
        self,
        source_rule: SourceRule,
        source_root: Path,
        destination_base: Path,
    ) -> Iterable[CopyPlanItem]:
        items: list[CopyPlanItem] = []
        for child in sorted(path for path in source_root.iterdir() if path.is_dir()):
            if source_rule.require_file and not (child / source_rule.require_file).exists():
                continue

            for path in sorted(p for p in child.rglob("*") if p.is_file()):
                relative = path.relative_to(child)
                destination = destination_base / child.name / self._normalize_relative_path(
                    relative,
                    source_rule.strip_suffix,
                )
                items.append(CopyPlanItem(path, destination))

        return items

    def _expand_tree_files(
        self,
        source_rule: SourceRule,
        source_root: Path,
        destination_base: Path,
    ) -> Iterable[CopyPlanItem]:
        items: list[CopyPlanItem] = []
        for path in sorted(p for p in source_root.rglob("*") if p.is_file()):
            relative = path.relative_to(source_root)
            relative_text = relative.as_posix()
            if not self._matches(relative_text, source_rule.include, default=True):
                continue
            if self._matches(relative_text, source_rule.exclude, default=False):
                continue

            destination = destination_base / self._normalize_relative_path(
                relative,
                source_rule.strip_suffix,
            )
            items.append(CopyPlanItem(path, destination))

        return items

    @staticmethod
    def _matches(path_text: str, patterns: tuple[str, ...], default: bool) -> bool:
        if not patterns:
            return default
        return any(fnmatch.fnmatch(path_text, pattern) for pattern in patterns)

    @staticmethod
    def _normalize_relative_path(relative: Path, strip_suffix: str | None) -> Path:
        if not strip_suffix:
            return relative

        relative_text = relative.as_posix()
        if relative_text.endswith(strip_suffix):
            relative_text = relative_text[: -len(strip_suffix)]
        return Path(relative_text)


class SyncExecutor:
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.copied = 0
        self.skipped = 0

    def run_rule(self, rule: SyncRule, plan: Iterable[CopyPlanItem]) -> None:
        for item in plan:
            self._sync_item(rule, item)

    def _sync_item(self, rule: SyncRule, item: CopyPlanItem) -> None:
        destination = item.destination.expanduser()
        source = item.source

        if destination.exists() and self._same_file(source, destination):
            self.skipped += 1
            if self.verbose:
                print(f"skip  {rule.name}: {destination}")
            return

        self.copied += 1
        action = "copy"
        print(f"{action}  {rule.name}: {source} -> {destination}")

        if self.dry_run:
            return

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    @staticmethod
    def _same_file(source: Path, destination: Path) -> bool:
        src_stat = source.stat()
        dst_stat = destination.stat()
        if src_stat.st_size != dst_stat.st_size:
            return False

        return source.read_bytes() == destination.read_bytes()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sync syncopated-context artifacts into local AI harness folders."
    )
    parser.add_argument(
        "--home",
        default=str(Path.home()),
        help="Home directory to sync into. Useful for dry-run testing.",
    )
    parser.add_argument(
        "--profile",
        action="append",
        choices=["gemini", "claude", "codex", "opencode", "crush"],
        help="Limit sync to one or more harness profiles.",
    )
    parser.add_argument(
        "--rule",
        action="append",
        help="Limit sync to one or more explicit rule names.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the planned copies without writing files.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print skipped files too.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    home_dir = Path(args.home).expanduser().resolve()
    rules = default_rules(home_dir)
    planner = SyncPlanner(rules)

    try:
        selected_rules = planner.select_rules(
            profiles=set(args.profile or []),
            rule_names=set(args.rule or []),
        )
    except SyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    executor = SyncExecutor(dry_run=args.dry_run, verbose=args.verbose)

    for rule in selected_rules:
        plan = planner.build_plan(rule)
        executor.run_rule(rule, plan)

    print(
        f"done: copied={executor.copied} skipped={executor.skipped} "
        f"mode={'dry-run' if args.dry_run else 'write'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
