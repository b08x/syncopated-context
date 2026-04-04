#!/usr/bin/env python3
"""
Ansible Collection Analyzer - Static analysis for collection structure and complexity
Provides detailed insights into collection architecture, file distribution, and metrics
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Tuple


class CollectionAnalyzer:
    """Analyzes Ansible collection structure and provides architectural insights"""
    
    def __init__(self, collection_path: str):
        self.collection_path = Path(collection_path).resolve()
        self.roles_path = self.collection_path / "roles"
        self.playbooks_path = self.collection_path / "playbooks"
        
        if not self.collection_path.exists():
            raise FileNotFoundError(f"Collection path not found: {collection_path}")
    
    def analyze_structure(self) -> Dict[str, Any]:
        """Analyze overall collection structure"""
        structure = {
            "collection_path": str(self.collection_path),
            "has_galaxy_yml": (self.collection_path / "galaxy.yml").exists(),
            "has_ansible_cfg": (self.collection_path / "ansible.cfg").exists(),
            "roles": self._analyze_roles(),
            "playbooks": self._analyze_playbooks(),
            "vars": self._analyze_vars(),
            "plugins": self._analyze_plugins(),
            "inventory": self._analyze_inventory(),
        }
        return structure
    
    def _analyze_roles(self) -> Dict[str, Any]:
        """Analyze roles directory structure"""
        if not self.roles_path.exists():
            return {"count": 0, "roles": []}
        
        roles = []
        for role_dir in sorted(self.roles_path.iterdir()):
            if role_dir.is_dir() and not role_dir.name.startswith('.'):
                role_info = {
                    "name": role_dir.name,
                    "path": str(role_dir.relative_to(self.collection_path)),
                    "structure": {},
                    "file_counts": {},
                }
                
                # Analyze role structure
                for subdir in ['tasks', 'defaults', 'vars', 'handlers', 'templates', 'files', 'meta']:
                    subdir_path = role_dir / subdir
                    if subdir_path.exists():
                        files = list(subdir_path.rglob('*'))
                        role_info["structure"][subdir] = True
                        role_info["file_counts"][subdir] = len([f for f in files if f.is_file()])
                
                # Check for metadata
                meta_path = role_dir / "meta" / "main.yml"
                if meta_path.exists():
                    try:
                        with open(meta_path) as f:
                            meta = yaml.safe_load(f)
                            if meta and "dependencies" in meta:
                                role_info["dependencies"] = meta["dependencies"]
                    except Exception as e:
                        role_info["meta_error"] = str(e)
                
                roles.append(role_info)
        
        return {
            "count": len(roles),
            "roles": roles
        }
    
    def _analyze_playbooks(self) -> Dict[str, Any]:
        """Analyze playbooks directory"""
        if not self.playbooks_path.exists():
            return {"count": 0, "playbooks": []}
        
        playbooks = []
        for pb_file in self.playbooks_path.glob("*.yml"):
            playbook_info = {
                "name": pb_file.name,
                "path": str(pb_file.relative_to(self.collection_path)),
                "size_lines": sum(1 for _ in open(pb_file)),
            }
            
            # Parse playbook to find roles
            try:
                with open(pb_file) as f:
                    pb_content = yaml.safe_load(f)
                    if isinstance(pb_content, list):
                        roles_called = []
                        for play in pb_content:
                            if isinstance(play, dict) and "roles" in play:
                                roles_called.extend(play["roles"])
                        playbook_info["roles_called"] = roles_called
            except Exception as e:
                playbook_info["parse_error"] = str(e)
            
            playbooks.append(playbook_info)
        
        return {
            "count": len(playbooks),
            "playbooks": playbooks
        }
    
    def _analyze_vars(self) -> Dict[str, Any]:
        """Analyze vars directory"""
        vars_path = self.collection_path / "vars"
        if not vars_path.exists():
            return {"exists": False}
        
        var_files = list(vars_path.glob("*.yml"))
        return {
            "exists": True,
            "file_count": len(var_files),
            "files": [f.name for f in var_files]
        }
    
    def _analyze_plugins(self) -> Dict[str, Any]:
        """Analyze plugins directory"""
        plugins_path = self.collection_path / "plugins"
        if not plugins_path.exists():
            return {"exists": False}
        
        plugin_types = {}
        for plugin_type_dir in plugins_path.iterdir():
            if plugin_type_dir.is_dir():
                plugins = list(plugin_type_dir.glob("*.py"))
                plugin_types[plugin_type_dir.name] = len(plugins)
        
        return {
            "exists": True,
            "types": plugin_types
        }
    
    def _analyze_inventory(self) -> Dict[str, Any]:
        """Analyze inventory directory"""
        inv_path = self.collection_path / "inventory"
        if not inv_path.exists():
            return {"exists": False}
        
        inv_files = list(inv_path.glob("*.ini")) + list(inv_path.glob("*.yml"))
        return {
            "exists": True,
            "file_count": len(inv_files)
        }
    
    def analyze_complexity(self) -> Dict[str, Any]:
        """Analyze collection complexity metrics"""
        metrics = {
            "total_files": 0,
            "yaml_files": 0,
            "yaml_lines": 0,
            "max_depth": 0,
            "large_files": [],  # Files > 100 lines
            "roles": {}
        }
        
        # Count all files and YAML
        for file_path in self.collection_path.rglob("*"):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                metrics["total_files"] += 1
                
                # Track directory depth
                depth = len(file_path.relative_to(self.collection_path).parts)
                metrics["max_depth"] = max(metrics["max_depth"], depth)
                
                # Analyze YAML files
                if file_path.suffix in ['.yml', '.yaml']:
                    metrics["yaml_files"] += 1
                    
                    try:
                        with open(file_path) as f:
                            lines = f.readlines()
                            line_count = len(lines)
                            metrics["yaml_lines"] += line_count
                            
                            # Track large files
                            if line_count > 100:
                                metrics["large_files"].append({
                                    "path": str(file_path.relative_to(self.collection_path)),
                                    "lines": line_count
                                })
                    except Exception:
                        pass
        
        # Sort large files by line count
        metrics["large_files"].sort(key=lambda x: x["lines"], reverse=True)
        
        # Analyze per-role complexity
        if self.roles_path.exists():
            for role_dir in self.roles_path.iterdir():
                if role_dir.is_dir() and not role_dir.name.startswith('.'):
                    role_metrics = {
                        "total_files": 0,
                        "yaml_lines": 0,
                        "max_depth": 0
                    }
                    
                    for file_path in role_dir.rglob("*"):
                        if file_path.is_file():
                            role_metrics["total_files"] += 1
                            
                            depth = len(file_path.relative_to(role_dir).parts)
                            role_metrics["max_depth"] = max(role_metrics["max_depth"], depth)
                            
                            if file_path.suffix in ['.yml', '.yaml']:
                                try:
                                    with open(file_path) as f:
                                        role_metrics["yaml_lines"] += len(f.readlines())
                                except Exception:
                                    pass
                    
                    metrics["roles"][role_dir.name] = role_metrics
        
        return metrics
    
    def generate_report(self, format: str = "text") -> str:
        """Generate comprehensive analysis report"""
        structure = self.analyze_structure()
        complexity = self.analyze_complexity()
        
        if format == "json":
            return json.dumps({
                "structure": structure,
                "complexity": complexity
            }, indent=2)
        
        # Text report
        lines = []
        lines.append("=" * 80)
        lines.append("ANSIBLE COLLECTION ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"\nCollection Path: {structure['collection_path']}")
        lines.append(f"galaxy.yml: {'✓' if structure['has_galaxy_yml'] else '✗'}")
        lines.append(f"ansible.cfg: {'✓' if structure['has_ansible_cfg'] else '✗'}")
        
        # Complexity Summary
        lines.append(f"\n{'=' * 80}")
        lines.append("COMPLEXITY METRICS")
        lines.append(f"{'=' * 80}")
        lines.append(f"Total Files: {complexity['total_files']}")
        lines.append(f"YAML Files: {complexity['yaml_files']}")
        lines.append(f"YAML Lines: {complexity['yaml_lines']}")
        lines.append(f"Max Directory Depth: {complexity['max_depth']}")
        lines.append(f"Large Files (>100 lines): {len(complexity['large_files'])}")
        
        # Large files
        if complexity['large_files']:
            lines.append(f"\n{'=' * 80}")
            lines.append("LARGE FILES (>100 lines)")
            lines.append(f"{'=' * 80}")
            for lf in complexity['large_files'][:10]:  # Top 10
                lines.append(f"  {lf['lines']:4d} lines: {lf['path']}")
        
        # Roles
        lines.append(f"\n{'=' * 80}")
        lines.append(f"ROLES ({structure['roles']['count']})")
        lines.append(f"{'=' * 80}")
        for role in structure['roles']['roles']:
            lines.append(f"\n{role['name']}:")
            lines.append(f"  Path: {role['path']}")
            if 'file_counts' in role:
                for subdir, count in sorted(role['file_counts'].items()):
                    lines.append(f"  {subdir:12s}: {count:3d} files")
            if 'dependencies' in role:
                lines.append(f"  Dependencies: {', '.join(str(d) for d in role['dependencies'])}")
            
            # Role complexity
            if role['name'] in complexity['roles']:
                rm = complexity['roles'][role['name']]
                lines.append(f"  Complexity: {rm['total_files']} files, {rm['yaml_lines']} YAML lines, depth {rm['max_depth']}")
        
        # Playbooks
        lines.append(f"\n{'=' * 80}")
        lines.append(f"PLAYBOOKS ({structure['playbooks']['count']})")
        lines.append(f"{'=' * 80}")
        for pb in structure['playbooks']['playbooks']:
            lines.append(f"\n{pb['name']}:")
            lines.append(f"  Lines: {pb['size_lines']}")
            if 'roles_called' in pb:
                lines.append(f"  Roles: {', '.join(str(r) for r in pb['roles_called'])}")
        
        # Plugins
        if structure['plugins']['exists']:
            lines.append(f"\n{'=' * 80}")
            lines.append("PLUGINS")
            lines.append(f"{'=' * 80}")
            for plugin_type, count in structure['plugins']['types'].items():
                lines.append(f"  {plugin_type}: {count}")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze Ansible collection structure and complexity")
    parser.add_argument("collection_path", help="Path to Ansible collection root")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    try:
        analyzer = CollectionAnalyzer(args.collection_path)
        report = analyzer.generate_report(format=args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Report written to {args.output}", file=sys.stderr)
        else:
            print(report)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
