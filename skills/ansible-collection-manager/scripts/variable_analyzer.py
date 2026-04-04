#!/usr/bin/env python3
"""
Variable Analyzer - Traces variable precedence and detects shadowing
Analyzes variable definitions across defaults, vars, group_vars, and host_vars
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional


class VariableAnalyzer:
    """Analyzes variable definitions and precedence across Ansible collection"""
    
    # Ansible variable precedence (simplified for collection analysis)
    # Lower number = lower precedence
    PRECEDENCE_LEVELS = {
        "role_defaults": 1,
        "inventory_group_vars": 2,
        "inventory_host_vars": 3,
        "role_vars": 4,
        "play_vars": 5,
        "extra_vars": 6,
    }
    
    def __init__(self, collection_path: str):
        self.collection_path = Path(collection_path).resolve()
        self.roles_path = self.collection_path / "roles"
        self.vars_path = self.collection_path / "vars"
        self.inventory_path = self.collection_path / "inventory"
        
        if not self.collection_path.exists():
            raise FileNotFoundError(f"Collection path not found: {collection_path}")
    
    def analyze_variables(self) -> Dict[str, Any]:
        """Analyze all variable definitions in the collection"""
        variables = defaultdict(lambda: {
            "definitions": [],
            "shadowed": False,
            "precedence_conflict": False
        })
        
        # Scan role defaults
        self._scan_role_defaults(variables)
        
        # Scan role vars
        self._scan_role_vars(variables)
        
        # Scan collection-level vars
        self._scan_collection_vars(variables)
        
        # Scan inventory vars
        self._scan_inventory_vars(variables)
        
        # Detect shadowing
        self._detect_shadowing(variables)
        
        return dict(variables)
    
    def _scan_role_defaults(self, variables: Dict):
        """Scan role defaults for variable definitions"""
        if not self.roles_path.exists():
            return
        
        for role_dir in self.roles_path.iterdir():
            if not role_dir.is_dir() or role_dir.name.startswith('.'):
                continue
            
            defaults_file = role_dir / "defaults" / "main.yml"
            if defaults_file.exists():
                self._extract_variables(
                    defaults_file,
                    variables,
                    "role_defaults",
                    {"role": role_dir.name}
                )
    
    def _scan_role_vars(self, variables: Dict):
        """Scan role vars for variable definitions"""
        if not self.roles_path.exists():
            return
        
        for role_dir in self.roles_path.iterdir():
            if not role_dir.is_dir() or role_dir.name.startswith('.'):
                continue
            
            vars_dir = role_dir / "vars"
            if vars_dir.exists():
                for var_file in vars_dir.glob("*.yml"):
                    self._extract_variables(
                        var_file,
                        variables,
                        "role_vars",
                        {"role": role_dir.name, "file": var_file.name}
                    )
    
    def _scan_collection_vars(self, variables: Dict):
        """Scan collection-level vars directory"""
        if not self.vars_path.exists():
            return
        
        for var_file in self.vars_path.glob("*.yml"):
            self._extract_variables(
                var_file,
                variables,
                "play_vars",  # Collection vars typically have high precedence
                {"file": var_file.name}
            )
    
    def _scan_inventory_vars(self, variables: Dict):
        """Scan inventory group_vars and host_vars"""
        if not self.inventory_path.exists():
            return
        
        # Group vars
        group_vars_path = self.inventory_path / "group_vars"
        if group_vars_path.exists():
            for var_file in group_vars_path.rglob("*.yml"):
                group_name = var_file.parent.name if var_file.parent != group_vars_path else var_file.stem
                self._extract_variables(
                    var_file,
                    variables,
                    "inventory_group_vars",
                    {"group": group_name}
                )
        
        # Host vars
        host_vars_path = self.inventory_path / "host_vars"
        if host_vars_path.exists():
            for var_file in host_vars_path.rglob("*.yml"):
                host_name = var_file.parent.name if var_file.parent != host_vars_path else var_file.stem
                self._extract_variables(
                    var_file,
                    variables,
                    "inventory_host_vars",
                    {"host": host_name}
                )
    
    def _extract_variables(self, file_path: Path, variables: Dict, 
                          source_type: str, context: Dict):
        """Extract variable definitions from a YAML file"""
        try:
            with open(file_path) as f:
                content = yaml.safe_load(f)
                
                if not content or not isinstance(content, dict):
                    return
                
                for var_name, var_value in content.items():
                    definition = {
                        "source_type": source_type,
                        "precedence": self.PRECEDENCE_LEVELS.get(source_type, 0),
                        "file": str(file_path.relative_to(self.collection_path)),
                        "context": context,
                        "value_type": type(var_value).__name__,
                        "is_secret": self._is_secret_variable(var_name, var_value),
                    }
                    
                    # Store sample value for non-secrets
                    if not definition["is_secret"]:
                        if isinstance(var_value, (str, int, bool, float)):
                            definition["sample_value"] = var_value
                        elif isinstance(var_value, list):
                            definition["sample_value"] = f"[list with {len(var_value)} items]"
                        elif isinstance(var_value, dict):
                            definition["sample_value"] = f"{{dict with {len(var_value)} keys}}"
                    
                    variables[var_name]["definitions"].append(definition)
        
        except Exception as e:
            pass
    
    def _is_secret_variable(self, var_name: str, var_value: Any) -> bool:
        """Check if a variable appears to be a secret"""
        secret_indicators = [
            'password', 'secret', 'token', 'key', 'credential',
            'passwd', 'api_key', 'private_key'
        ]
        
        var_lower = var_name.lower()
        return any(indicator in var_lower for indicator in secret_indicators)
    
    def _detect_shadowing(self, variables: Dict):
        """Detect variable shadowing (same var defined at multiple precedence levels)"""
        for var_name, var_info in variables.items():
            definitions = var_info["definitions"]
            
            if len(definitions) > 1:
                # Check if multiple precedence levels
                precedence_levels = set(d["precedence"] for d in definitions)
                if len(precedence_levels) > 1:
                    var_info["shadowed"] = True
                    var_info["precedence_conflict"] = True
                    
                    # Identify which definition wins
                    winning_def = max(definitions, key=lambda d: d["precedence"])
                    var_info["winning_definition"] = winning_def
    
    def find_variable_usage(self, var_name: str) -> List[Dict[str, Any]]:
        """Find where a variable is used in tasks"""
        usages = []
        
        # Search through all task files
        for task_file in self.collection_path.rglob("tasks/**/*.yml"):
            try:
                with open(task_file) as f:
                    content = f.read()
                    
                    # Look for Jinja2 variable references
                    if f"{{{{ {var_name} }}}}" in content or f"{{{{ {var_name}." in content:
                        usages.append({
                            "file": str(task_file.relative_to(self.collection_path)),
                            "type": "jinja2"
                        })
                    
                    # Look for direct references in when clauses etc
                    if var_name in content:
                        # Parse YAML to check if it's actually used
                        try:
                            yaml_content = yaml.safe_load(content)
                            if self._variable_in_structure(var_name, yaml_content):
                                if {
                                    "file": str(task_file.relative_to(self.collection_path)),
                                    "type": "direct"
                                } not in usages:
                                    usages.append({
                                        "file": str(task_file.relative_to(self.collection_path)),
                                        "type": "direct"
                                    })
                        except:
                            pass
            except Exception:
                pass
        
        return usages
    
    def _variable_in_structure(self, var_name: str, structure: Any) -> bool:
        """Recursively check if variable is referenced in data structure"""
        if isinstance(structure, str):
            return var_name in structure
        elif isinstance(structure, dict):
            return any(self._variable_in_structure(var_name, v) for v in structure.values())
        elif isinstance(structure, list):
            return any(self._variable_in_structure(var_name, item) for item in structure)
        return False
    
    def generate_report(self, format: str = "text", 
                       show_shadowed_only: bool = False,
                       variable_name: Optional[str] = None) -> str:
        """Generate variable analysis report"""
        variables = self.analyze_variables()
        
        if variable_name:
            # Report on specific variable
            if variable_name not in variables:
                return f"Variable '{variable_name}' not found in collection"
            
            var_info = variables[variable_name]
            usages = self.find_variable_usage(variable_name)
            
            if format == "json":
                return json.dumps({
                    "variable": variable_name,
                    "info": var_info,
                    "usages": usages
                }, indent=2)
            
            lines = []
            lines.append("=" * 80)
            lines.append(f"VARIABLE ANALYSIS: {variable_name}")
            lines.append("=" * 80)
            
            lines.append(f"\nDefinitions ({len(var_info['definitions'])}):")
            for defn in sorted(var_info['definitions'], key=lambda d: d['precedence']):
                lines.append(f"\n  [{defn['source_type']}] Precedence: {defn['precedence']}")
                lines.append(f"  File: {defn['file']}")
                if "role" in defn['context']:
                    lines.append(f"  Role: {defn['context']['role']}")
                if "sample_value" in defn and not defn['is_secret']:
                    lines.append(f"  Value: {defn['sample_value']}")
                if defn['is_secret']:
                    lines.append(f"  Value: [REDACTED - appears to be secret]")
            
            if var_info['shadowed']:
                lines.append(f"\n⚠️  SHADOWING DETECTED")
                lines.append(f"  Winning definition: {var_info['winning_definition']['source_type']}")
                lines.append(f"  File: {var_info['winning_definition']['file']}")
            
            if usages:
                lines.append(f"\nUsages ({len(usages)}):")
                for usage in usages:
                    lines.append(f"  - {usage['file']} ({usage['type']})")
            
            return "\n".join(lines)
        
        # Full report
        if format == "json":
            return json.dumps(variables, indent=2)
        
        lines = []
        lines.append("=" * 80)
        lines.append("VARIABLE ANALYSIS REPORT")
        lines.append("=" * 80)
        
        # Filter variables
        if show_shadowed_only:
            variables = {k: v for k, v in variables.items() if v["shadowed"]}
        
        # Summary
        total_vars = len(variables)
        shadowed_vars = sum(1 for v in variables.values() if v["shadowed"])
        secret_vars = sum(1 for v in variables.values() 
                         if any(d["is_secret"] for d in v["definitions"]))
        
        lines.append(f"\nSUMMARY:")
        lines.append(f"  Total Variables: {total_vars}")
        lines.append(f"  Shadowed Variables: {shadowed_vars}")
        lines.append(f"  Secret Variables: {secret_vars}")
        
        # Shadowed variables
        if shadowed_vars > 0:
            lines.append(f"\n{'=' * 80}")
            lines.append(f"SHADOWED VARIABLES ({shadowed_vars})")
            lines.append(f"{'=' * 80}")
            
            for var_name, var_info in sorted(variables.items()):
                if var_info["shadowed"]:
                    lines.append(f"\n{var_name}:")
                    lines.append(f"  Definitions: {len(var_info['definitions'])}")
                    
                    for defn in sorted(var_info['definitions'], key=lambda d: d['precedence']):
                        marker = "→" if defn == var_info.get("winning_definition") else " "
                        lines.append(f"  {marker} [{defn['source_type']}] {defn['file']}")
        
        # Variables by source type
        if not show_shadowed_only:
            by_source = defaultdict(list)
            for var_name, var_info in variables.items():
                for defn in var_info["definitions"]:
                    by_source[defn["source_type"]].append(var_name)
            
            lines.append(f"\n{'=' * 80}")
            lines.append(f"VARIABLES BY SOURCE TYPE")
            lines.append(f"{'=' * 80}")
            
            for source_type in sorted(by_source.keys()):
                vars_in_source = by_source[source_type]
                lines.append(f"\n{source_type}: {len(vars_in_source)} variables")
                if len(vars_in_source) <= 20:
                    for var in sorted(vars_in_source):
                        lines.append(f"  - {var}")
                else:
                    for var in sorted(vars_in_source)[:10]:
                        lines.append(f"  - {var}")
                    lines.append(f"  ... and {len(vars_in_source) - 10} more")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze Ansible variable definitions and precedence")
    parser.add_argument("collection_path", help="Path to Ansible collection root")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--shadowed-only", action="store_true",
                        help="Show only shadowed variables")
    parser.add_argument("--variable", "-v", help="Analyze specific variable")
    
    args = parser.parse_args()
    
    try:
        analyzer = VariableAnalyzer(args.collection_path)
        report = analyzer.generate_report(
            format=args.format,
            show_shadowed_only=args.shadowed_only,
            variable_name=args.variable
        )
        
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
