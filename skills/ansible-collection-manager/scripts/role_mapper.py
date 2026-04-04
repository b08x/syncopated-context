#!/usr/bin/env python3
"""
Role Dependency Mapper - Maps role dependencies and generates call graphs
Analyzes meta/main.yml dependencies and playbook role inclusions
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, List, Any, Set, Tuple


class RoleDependencyMapper:
    """Maps role dependencies and generates dependency graphs"""
    
    def __init__(self, collection_path: str):
        self.collection_path = Path(collection_path).resolve()
        self.roles_path = self.collection_path / "roles"
        self.playbooks_path = self.collection_path / "playbooks"
        
        if not self.collection_path.exists():
            raise FileNotFoundError(f"Collection path not found: {collection_path}")
    
    def map_dependencies(self) -> Dict[str, Any]:
        """Map all role dependencies in the collection"""
        role_info = {}
        
        # Scan all roles
        if self.roles_path.exists():
            for role_dir in self.roles_path.iterdir():
                if not role_dir.is_dir() or role_dir.name.startswith('.'):
                    continue
                
                role_name = role_dir.name
                role_info[role_name] = {
                    "path": str(role_dir.relative_to(self.collection_path)),
                    "depends_on": [],
                    "depended_by": [],
                    "used_in_playbooks": [],
                }
                
                # Parse meta/main.yml for dependencies
                meta_file = role_dir / "meta" / "main.yml"
                if meta_file.exists():
                    try:
                        with open(meta_file) as f:
                            meta = yaml.safe_load(f)
                            if meta and "dependencies" in meta:
                                deps = meta["dependencies"]
                                if isinstance(deps, list):
                                    for dep in deps:
                                        dep_name = self._extract_role_name(dep)
                                        if dep_name:
                                            role_info[role_name]["depends_on"].append(dep_name)
                    except Exception as e:
                        role_info[role_name]["meta_error"] = str(e)
        
        # Build reverse dependency map
        for role_name, info in role_info.items():
            for dep_name in info["depends_on"]:
                if dep_name in role_info:
                    role_info[dep_name]["depended_by"].append(role_name)
        
        # Find playbook usage
        if self.playbooks_path.exists():
            for playbook_file in self.playbooks_path.glob("*.yml"):
                playbook_roles = self._extract_playbook_roles(playbook_file)
                for role_name in playbook_roles:
                    if role_name in role_info:
                        role_info[role_name]["used_in_playbooks"].append(playbook_file.name)
        
        return role_info
    
    def _extract_role_name(self, dep: Any) -> str:
        """Extract role name from dependency specification"""
        if isinstance(dep, str):
            # Simple string dependency
            return dep.split('.')[-1]  # Handle FQCN
        elif isinstance(dep, dict):
            # Dict with role key
            if "role" in dep:
                role = dep["role"]
                if isinstance(role, str):
                    return role.split('.')[-1]
        return None
    
    def _extract_playbook_roles(self, playbook_file: Path) -> List[str]:
        """Extract roles called in a playbook"""
        roles = []
        
        try:
            with open(playbook_file) as f:
                content = yaml.safe_load(f)
                
                if isinstance(content, list):
                    for play in content:
                        if isinstance(play, dict):
                            # Direct roles list
                            if "roles" in play:
                                play_roles = play["roles"]
                                if isinstance(play_roles, list):
                                    for role in play_roles:
                                        role_name = self._extract_role_name(role)
                                        if role_name:
                                            roles.append(role_name)
                            
                            # Role in tasks with include_role
                            if "tasks" in play:
                                tasks = play["tasks"]
                                if isinstance(tasks, list):
                                    for task in tasks:
                                        if isinstance(task, dict):
                                            if "include_role" in task or "import_role" in task:
                                                role_spec = task.get("include_role") or task.get("import_role")
                                                if isinstance(role_spec, dict) and "name" in role_spec:
                                                    role_name = role_spec["name"]
                                                    if isinstance(role_name, str):
                                                        roles.append(role_name.split('.')[-1])
        
        except Exception:
            pass
        
        return roles
    
    def detect_circular_dependencies(self, role_info: Dict[str, Any]) -> List[List[str]]:
        """Detect circular dependencies between roles"""
        cycles = []
        
        def find_cycles(role: str, path: List[str], visited: Set[str]) -> None:
            if role in path:
                # Found a cycle
                cycle_start = path.index(role)
                cycle = path[cycle_start:] + [role]
                cycles.append(cycle)
                return
            
            if role in visited:
                return
            
            visited.add(role)
            path.append(role)
            
            for dep in role_info.get(role, {}).get("depends_on", []):
                find_cycles(dep, path.copy(), visited)
        
        for role_name in role_info.keys():
            find_cycles(role_name, [], set())
        
        # Remove duplicate cycles
        unique_cycles = []
        for cycle in cycles:
            # Normalize cycle to start with smallest name
            min_idx = cycle.index(min(cycle))
            normalized = cycle[min_idx:] + cycle[:min_idx]
            if normalized not in unique_cycles:
                unique_cycles.append(normalized)
        
        return unique_cycles
    
    def find_orphaned_roles(self, role_info: Dict[str, Any]) -> List[str]:
        """Find roles that are never used"""
        orphaned = []
        
        for role_name, info in role_info.items():
            # Role is orphaned if:
            # 1. Not used in any playbook
            # 2. Not depended on by any other role
            if not info["used_in_playbooks"] and not info["depended_by"]:
                orphaned.append(role_name)
        
        return orphaned
    
    def calculate_dependency_depth(self, role_info: Dict[str, Any]) -> Dict[str, int]:
        """Calculate dependency depth for each role (longest chain)"""
        depths = {}
        
        def get_depth(role: str, visited: Set[str] = None) -> int:
            if visited is None:
                visited = set()
            
            if role in depths:
                return depths[role]
            
            if role in visited:
                # Circular dependency
                return 0
            
            if role not in role_info:
                return 0
            
            visited.add(role)
            
            depends_on = role_info[role].get("depends_on", [])
            if not depends_on:
                depth = 0
            else:
                depth = 1 + max(get_depth(dep, visited.copy()) for dep in depends_on)
            
            depths[role] = depth
            return depth
        
        for role_name in role_info.keys():
            get_depth(role_name)
        
        return depths
    
    def generate_mermaid_graph(self, role_info: Dict[str, Any], 
                              include_playbooks: bool = True) -> str:
        """Generate Mermaid flowchart diagram"""
        lines = ["graph TD"]
        
        # Add roles
        for role_name in role_info.keys():
            lines.append(f"    {role_name}[{role_name}]")
        
        # Add dependencies
        for role_name, info in role_info.items():
            for dep in info["depends_on"]:
                lines.append(f"    {role_name} --> {dep}")
        
        # Add playbooks if requested
        if include_playbooks:
            playbook_roles = defaultdict(list)
            for role_name, info in role_info.items():
                for playbook in info["used_in_playbooks"]:
                    playbook_roles[playbook].append(role_name)
            
            for playbook, roles in playbook_roles.items():
                pb_id = playbook.replace('.', '_').replace('-', '_')
                lines.append(f"    {pb_id}{{{{playbook: {playbook}}}}}")
                for role in roles:
                    lines.append(f"    {pb_id} -.-> {role}")
        
        return "\n".join(lines)
    
    def generate_report(self, format: str = "text", 
                       include_graph: bool = False) -> str:
        """Generate dependency analysis report"""
        role_info = self.map_dependencies()
        circular_deps = self.detect_circular_dependencies(role_info)
        orphaned_roles = self.find_orphaned_roles(role_info)
        depths = self.calculate_dependency_depth(role_info)
        
        if format == "json":
            return json.dumps({
                "roles": role_info,
                "circular_dependencies": circular_deps,
                "orphaned_roles": orphaned_roles,
                "dependency_depths": depths,
            }, indent=2)
        
        # Text report
        lines = []
        lines.append("=" * 80)
        lines.append("ROLE DEPENDENCY ANALYSIS")
        lines.append("=" * 80)
        
        lines.append(f"\nSUMMARY:")
        lines.append(f"  Total Roles: {len(role_info)}")
        lines.append(f"  Circular Dependencies: {len(circular_deps)}")
        lines.append(f"  Orphaned Roles: {len(orphaned_roles)}")
        lines.append(f"  Max Dependency Depth: {max(depths.values()) if depths else 0}")
        
        # Circular dependencies
        if circular_deps:
            lines.append(f"\n{'=' * 80}")
            lines.append(f"⚠️  CIRCULAR DEPENDENCIES DETECTED ({len(circular_deps)})")
            lines.append(f"{'=' * 80}")
            
            for i, cycle in enumerate(circular_deps, 1):
                lines.append(f"\nCycle {i}: {' → '.join(cycle)}")
        
        # Orphaned roles
        if orphaned_roles:
            lines.append(f"\n{'=' * 80}")
            lines.append(f"ORPHANED ROLES (never used) ({len(orphaned_roles)})")
            lines.append(f"{'=' * 80}")
            
            for role in sorted(orphaned_roles):
                lines.append(f"  - {role}")
        
        # Dependency depth analysis
        lines.append(f"\n{'=' * 80}")
        lines.append(f"ROLES BY DEPENDENCY DEPTH")
        lines.append(f"{'=' * 80}")
        
        by_depth = defaultdict(list)
        for role, depth in depths.items():
            by_depth[depth].append(role)
        
        for depth in sorted(by_depth.keys(), reverse=True):
            roles = by_depth[depth]
            lines.append(f"\nDepth {depth} ({len(roles)} roles):")
            for role in sorted(roles):
                lines.append(f"  - {role}")
        
        # Role details
        lines.append(f"\n{'=' * 80}")
        lines.append(f"ROLE DEPENDENCY DETAILS")
        lines.append(f"{'=' * 80}")
        
        for role_name in sorted(role_info.keys()):
            info = role_info[role_name]
            lines.append(f"\n{role_name}:")
            lines.append(f"  Path: {info['path']}")
            lines.append(f"  Dependency Depth: {depths.get(role_name, 0)}")
            
            if info["depends_on"]:
                lines.append(f"  Depends On: {', '.join(info['depends_on'])}")
            else:
                lines.append(f"  Depends On: (none)")
            
            if info["depended_by"]:
                lines.append(f"  Depended By: {', '.join(info['depended_by'])}")
            
            if info["used_in_playbooks"]:
                lines.append(f"  Used In Playbooks: {', '.join(info['used_in_playbooks'])}")
            elif not info["depended_by"]:
                lines.append(f"  ⚠️  Never used (orphaned)")
        
        # Mermaid graph
        if include_graph:
            lines.append(f"\n{'=' * 80}")
            lines.append(f"DEPENDENCY GRAPH (Mermaid)")
            lines.append(f"{'=' * 80}")
            lines.append("\n```mermaid")
            lines.append(self.generate_mermaid_graph(role_info))
            lines.append("```")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Map Ansible role dependencies")
    parser.add_argument("collection_path", help="Path to Ansible collection root")
    parser.add_argument("--format", choices=["text", "json", "mermaid"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--graph", action="store_true",
                        help="Include Mermaid graph in text output")
    
    args = parser.parse_args()
    
    try:
        mapper = RoleDependencyMapper(args.collection_path)
        
        if args.format == "mermaid":
            role_info = mapper.map_dependencies()
            report = mapper.generate_mermaid_graph(role_info)
        else:
            report = mapper.generate_report(format=args.format, include_graph=args.graph)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Report written to {args.output}", file=sys.stderr)
        else:
            print(report)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
