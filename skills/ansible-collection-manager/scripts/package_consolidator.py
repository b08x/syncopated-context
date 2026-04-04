#!/usr/bin/env python3
"""
Package Consolidator - Identifies package duplication across Ansible roles
Helps prepare consolidated package lists for refactoring
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Set


class PackageConsolidator:
    """Analyzes package definitions across roles and identifies consolidation opportunities"""
    
    def __init__(self, collection_path: str):
        self.collection_path = Path(collection_path).resolve()
        self.roles_path = self.collection_path / "roles"
        
        if not self.collection_path.exists():
            raise FileNotFoundError(f"Collection path not found: {collection_path}")
    
    def analyze_packages(self) -> Dict[str, Any]:
        """Analyze package definitions across all roles"""
        package_locations = defaultdict(list)
        role_packages = {}
        
        # Scan all roles for package definitions
        if self.roles_path.exists():
            for role_dir in self.roles_path.iterdir():
                if not role_dir.is_dir() or role_dir.name.startswith('.'):
                    continue
                
                role_name = role_dir.name
                packages = self._extract_packages_from_role(role_dir)
                
                if packages:
                    role_packages[role_name] = packages
                    
                    # Track where each package is defined
                    for pkg in packages:
                        package_locations[pkg].append(role_name)
        
        # Identify duplicated packages
        duplicated_packages = {
            pkg: roles for pkg, roles in package_locations.items()
            if len(roles) > 1
        }
        
        # Categorize packages by duplication level
        highly_duplicated = {  # 5+ roles
            pkg: roles for pkg, roles in duplicated_packages.items()
            if len(roles) >= 5
        }
        
        moderately_duplicated = {  # 3-4 roles
            pkg: roles for pkg, roles in duplicated_packages.items()
            if 3 <= len(roles) < 5
        }
        
        slightly_duplicated = {  # 2 roles
            pkg: roles for pkg, roles in duplicated_packages.items()
            if len(roles) == 2
        }
        
        return {
            "total_roles": len(role_packages),
            "total_unique_packages": len(package_locations),
            "duplicated_packages_count": len(duplicated_packages),
            "role_packages": role_packages,
            "package_locations": dict(package_locations),
            "duplicated_packages": duplicated_packages,
            "highly_duplicated": highly_duplicated,
            "moderately_duplicated": moderately_duplicated,
            "slightly_duplicated": slightly_duplicated,
        }
    
    def _extract_packages_from_role(self, role_dir: Path) -> Set[str]:
        """Extract all package names from a role's defaults and vars"""
        packages = set()
        
        # Check defaults/main.yml
        defaults_file = role_dir / "defaults" / "main.yml"
        if defaults_file.exists():
            packages.update(self._extract_packages_from_file(defaults_file))
        
        # Check vars/*.yml
        vars_dir = role_dir / "vars"
        if vars_dir.exists():
            for var_file in vars_dir.glob("*.yml"):
                packages.update(self._extract_packages_from_file(var_file))
        
        # Check tasks for inline package definitions
        tasks_dir = role_dir / "tasks"
        if tasks_dir.exists():
            for task_file in tasks_dir.rglob("*.yml"):
                packages.update(self._extract_packages_from_tasks(task_file))
        
        return packages
    
    def _extract_packages_from_file(self, file_path: Path) -> Set[str]:
        """Extract package names from a YAML file"""
        packages = set()
        
        try:
            with open(file_path) as f:
                content = yaml.safe_load(f)
                
                if not content:
                    return packages
                
                # Look for variables that contain package lists
                for key, value in content.items():
                    if self._is_package_variable(key):
                        packages.update(self._extract_package_names(value))
        
        except Exception:
            pass
        
        return packages
    
    def _extract_packages_from_tasks(self, task_file: Path) -> Set[str]:
        """Extract package names from task definitions"""
        packages = set()
        
        try:
            with open(task_file) as f:
                content = yaml.safe_load(f)
                
                if not content:
                    return packages
                
                # Parse tasks
                if isinstance(content, list):
                    for task in content:
                        if isinstance(task, dict):
                            # Look for package module usage
                            for module in ['dnf', 'yum', 'package', 'apt']:
                                if module in task or f'ansible.builtin.{module}' in task:
                                    module_params = task.get(module) or task.get(f'ansible.builtin.{module}')
                                    if isinstance(module_params, dict):
                                        name_param = module_params.get('name')
                                        packages.update(self._extract_package_names(name_param))
        
        except Exception:
            pass
        
        return packages
    
    def _is_package_variable(self, var_name: str) -> bool:
        """Check if a variable name suggests it contains packages"""
        package_indicators = ['package', 'pkg', 'packages', 'pkgs', 'install', 'dependencies']
        var_lower = var_name.lower()
        return any(indicator in var_lower for indicator in package_indicators)
    
    def _extract_package_names(self, value: Any) -> Set[str]:
        """Extract package names from various data structures"""
        packages = set()
        
        if isinstance(value, str):
            packages.add(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    packages.add(item)
                elif isinstance(item, dict):
                    # Handle dict format like {name: pkg, state: present}
                    if 'name' in item:
                        name = item['name']
                        if isinstance(name, str):
                            packages.add(name)
                        elif isinstance(name, list):
                            packages.update(name)
        
        return packages
    
    def generate_consolidation_plan(self) -> Dict[str, Any]:
        """Generate a consolidation plan for duplicated packages"""
        analysis = self.analyze_packages()
        
        plan = {
            "recommended_common_packages": [],
            "role_specific_packages": {},
            "consolidation_steps": []
        }
        
        # Highly duplicated packages should move to common
        if analysis["highly_duplicated"]:
            plan["recommended_common_packages"] = sorted(analysis["highly_duplicated"].keys())
            plan["consolidation_steps"].append({
                "step": 1,
                "action": "Create common/vars/packages.yml",
                "packages": plan["recommended_common_packages"],
                "reason": f"{len(plan['recommended_common_packages'])} packages used in 5+ roles"
            })
        
        # For each role, identify packages to keep vs move
        for role_name, packages in analysis["role_packages"].items():
            role_specific = []
            to_remove = []
            
            for pkg in packages:
                if pkg in analysis["highly_duplicated"]:
                    to_remove.append(pkg)
                else:
                    role_specific.append(pkg)
            
            if to_remove:
                plan["role_specific_packages"][role_name] = {
                    "keep": sorted(role_specific),
                    "remove": sorted(to_remove),
                }
        
        return plan
    
    def generate_report(self, format: str = "text", include_plan: bool = False) -> str:
        """Generate package consolidation report"""
        analysis = self.analyze_packages()
        
        if format == "json":
            if include_plan:
                analysis["consolidation_plan"] = self.generate_consolidation_plan()
            return json.dumps(analysis, indent=2)
        
        # Text report
        lines = []
        lines.append("=" * 80)
        lines.append("PACKAGE CONSOLIDATION ANALYSIS")
        lines.append("=" * 80)
        
        lines.append(f"\nSUMMARY:")
        lines.append(f"  Total Roles Analyzed: {analysis['total_roles']}")
        lines.append(f"  Total Unique Packages: {analysis['total_unique_packages']}")
        lines.append(f"  Duplicated Packages: {analysis['duplicated_packages_count']}")
        lines.append(f"    - Highly Duplicated (5+ roles): {len(analysis['highly_duplicated'])}")
        lines.append(f"    - Moderately Duplicated (3-4 roles): {len(analysis['moderately_duplicated'])}")
        lines.append(f"    - Slightly Duplicated (2 roles): {len(analysis['slightly_duplicated'])}")
        
        # Highly duplicated packages
        if analysis["highly_duplicated"]:
            lines.append(f"\n{'=' * 80}")
            lines.append(f"HIGHLY DUPLICATED PACKAGES (5+ roles) - CONSOLIDATION PRIORITY")
            lines.append(f"{'=' * 80}")
            
            for pkg, roles in sorted(analysis["highly_duplicated"].items(), 
                                    key=lambda x: len(x[1]), reverse=True):
                lines.append(f"\n{pkg} ({len(roles)} roles):")
                for role in sorted(roles):
                    lines.append(f"  - {role}")
        
        # Moderately duplicated packages
        if analysis["moderately_duplicated"]:
            lines.append(f"\n{'=' * 80}")
            lines.append(f"MODERATELY DUPLICATED PACKAGES (3-4 roles)")
            lines.append(f"{'=' * 80}")
            
            for pkg, roles in sorted(analysis["moderately_duplicated"].items(),
                                    key=lambda x: len(x[1]), reverse=True):
                lines.append(f"\n{pkg} ({len(roles)} roles): {', '.join(sorted(roles))}")
        
        # Consolidation plan
        if include_plan:
            plan = self.generate_consolidation_plan()
            
            lines.append(f"\n{'=' * 80}")
            lines.append(f"CONSOLIDATION PLAN")
            lines.append(f"{'=' * 80}")
            
            if plan["recommended_common_packages"]:
                lines.append(f"\nRECOMMENDED FOR common/vars/packages.yml:")
                for pkg in plan["recommended_common_packages"]:
                    roles = analysis["highly_duplicated"][pkg]
                    lines.append(f"  - {pkg} (currently in: {', '.join(sorted(roles))})")
                
                lines.append(f"\nTOTAL PACKAGES TO CONSOLIDATE: {len(plan['recommended_common_packages'])}")
            
            # Per-role cleanup
            if plan["role_specific_packages"]:
                lines.append(f"\n{'=' * 80}")
                lines.append(f"PER-ROLE CLEANUP ACTIONS")
                lines.append(f"{'=' * 80}")
                
                for role_name, actions in sorted(plan["role_specific_packages"].items()):
                    if actions["remove"]:
                        lines.append(f"\n{role_name}:")
                        lines.append(f"  Remove {len(actions['remove'])} packages (moving to common):")
                        for pkg in actions["remove"][:10]:  # Show first 10
                            lines.append(f"    - {pkg}")
                        if len(actions["remove"]) > 10:
                            lines.append(f"    ... and {len(actions['remove']) - 10} more")
                        lines.append(f"  Keep {len(actions['keep'])} role-specific packages")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze and consolidate package definitions")
    parser.add_argument("collection_path", help="Path to Ansible collection root")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--plan", action="store_true",
                        help="Include consolidation plan in output")
    
    args = parser.parse_args()
    
    try:
        consolidator = PackageConsolidator(args.collection_path)
        report = consolidator.generate_report(format=args.format, include_plan=args.plan)
        
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
