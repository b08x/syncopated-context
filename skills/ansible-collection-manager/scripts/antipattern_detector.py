#!/usr/bin/env python3
"""
Ansible Anti-Pattern Detector - Identifies security issues and code smells
Focuses on common issues in Ansible collections including security vulnerabilities
"""

import os
import sys
import yaml
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict


class AntiPatternDetector:
    """Detects anti-patterns, security issues, and code smells in Ansible collections"""
    
    # Security-critical patterns
    SECURITY_PATTERNS = {
        "unencrypted_secrets": {
            "description": "Potential unencrypted secrets in vars/",
            "severity": "CRITICAL",
            "patterns": [
                r"password\s*:",
                r"secret\s*:",
                r"token\s*:",
                r"api_key\s*:",
                r"credential\s*:",
            ]
        },
        "smb1_protocol": {
            "description": "SMB1 protocol enabled (deprecated, insecure)",
            "severity": "HIGH",
            "patterns": [r"SMB1", r"min_protocol.*SMB1", r"NTLMv1"]
        },
        "empty_password": {
            "description": "Empty or default passwords",
            "severity": "CRITICAL",
            "patterns": [
                r'password\s*:\s*["\']?\s*["\']?',
                r'password\s*:\s*""',
                r"password\s*:\s*''",
            ]
        },
        "shell_without_validation": {
            "description": "Shell/command usage without input validation",
            "severity": "MEDIUM",
            "patterns": [
                r"ansible\.builtin\.shell",
                r"ansible\.builtin\.command",
                r"module:\s*shell",
                r"module:\s*command"
            ]
        },
        "sudo_without_password": {
            "description": "Sudo without password requirements",
            "severity": "HIGH",
            "patterns": [r"NOPASSWD", r"!authenticate"]
        },
        "root_equivalent": {
            "description": "Granting root-equivalent privileges",
            "severity": "HIGH",
            "patterns": [
                r"groups?:\s*.*\b(docker|libvirt|wheel)\b",
                r"state:\s*present.*groups?:.*docker"
            ]
        }
    }
    
    # Code quality anti-patterns
    CODE_PATTERNS = {
        "templates_in_files": {
            "description": "Templates placed in files/ instead of templates/",
            "severity": "MEDIUM",
        },
        "monolithic_defaults": {
            "description": "Defaults file exceeds 200 lines",
            "severity": "MEDIUM",
            "threshold": 200
        },
        "hardcoded_timeout": {
            "description": "Hardcoded timeout values",
            "severity": "LOW",
            "patterns": [r"timeout:\s*\d{4,}", r"async:\s*\d{4,}"]
        },
        "stdout_parsing": {
            "description": "Parsing stdout instead of structured output",
            "severity": "MEDIUM",
            "patterns": [r"stdout_lines", r"stdout\s*\|", r"register:.*stdout"]
        },
        "no_changed_when": {
            "description": "Shell/command without changed_when",
            "severity": "LOW",
        }
    }
    
    def __init__(self, collection_path: str):
        self.collection_path = Path(collection_path).resolve()
        self.findings = defaultdict(list)
        
        if not self.collection_path.exists():
            raise FileNotFoundError(f"Collection path not found: {collection_path}")
    
    def scan(self) -> Dict[str, List[Dict[str, Any]]]:
        """Run all anti-pattern scans"""
        self._scan_security_issues()
        self._scan_code_quality()
        self._scan_structural_issues()
        return dict(self.findings)
    
    def _scan_security_issues(self):
        """Scan for security vulnerabilities"""
        # Scan vars directory for unencrypted secrets
        vars_path = self.collection_path / "vars"
        if vars_path.exists():
            for var_file in vars_path.glob("*.yml"):
                if "vault" not in var_file.name.lower():
                    self._check_file_for_patterns(
                        var_file, 
                        "unencrypted_secrets",
                        self.SECURITY_PATTERNS["unencrypted_secrets"]
                    )
        
        # Scan all YAML files for other security patterns
        for yaml_file in self.collection_path.rglob("*.yml"):
            # Skip hidden files
            if any(part.startswith('.') for part in yaml_file.parts):
                continue
            
            # Check for SMB1/NTLMv1
            if "nas" in str(yaml_file) or "samba" in str(yaml_file):
                self._check_file_for_patterns(
                    yaml_file,
                    "smb1_protocol",
                    self.SECURITY_PATTERNS["smb1_protocol"]
                )
            
            # Check for empty passwords
            self._check_file_for_patterns(
                yaml_file,
                "empty_password",
                self.SECURITY_PATTERNS["empty_password"]
            )
            
            # Check for shell usage
            self._check_file_for_patterns(
                yaml_file,
                "shell_without_validation",
                self.SECURITY_PATTERNS["shell_without_validation"]
            )
            
            # Check for root-equivalent groups
            self._check_file_for_patterns(
                yaml_file,
                "root_equivalent",
                self.SECURITY_PATTERNS["root_equivalent"]
            )
    
    def _scan_code_quality(self):
        """Scan for code quality issues"""
        # Check for templates in files/
        for role_dir in (self.collection_path / "roles").iterdir():
            if not role_dir.is_dir():
                continue
            
            files_dir = role_dir / "files"
            if files_dir.exists():
                # Look for template-like patterns
                for file_path in files_dir.rglob("*"):
                    if file_path.is_file():
                        try:
                            with open(file_path) as f:
                                content = f.read(1000)  # First 1000 chars
                                if "{{" in content and "}}" in content:
                                    self.findings["templates_in_files"].append({
                                        "severity": "MEDIUM",
                                        "file": str(file_path.relative_to(self.collection_path)),
                                        "description": "File in files/ contains Jinja2 templates"
                                    })
                        except Exception:
                            pass
        
        # Check for monolithic defaults
        for defaults_file in self.collection_path.rglob("defaults/main.yml"):
            try:
                with open(defaults_file) as f:
                    lines = len(f.readlines())
                    if lines > 200:
                        self.findings["monolithic_defaults"].append({
                            "severity": "MEDIUM",
                            "file": str(defaults_file.relative_to(self.collection_path)),
                            "lines": lines,
                            "description": f"Defaults file with {lines} lines (>200 threshold)"
                        })
            except Exception:
                pass
        
        # Check for hardcoded timeouts and stdout parsing
        for yaml_file in self.collection_path.rglob("*.yml"):
            if any(part.startswith('.') for part in yaml_file.parts):
                continue
            
            self._check_file_for_patterns(
                yaml_file,
                "hardcoded_timeout",
                self.CODE_PATTERNS["hardcoded_timeout"]
            )
            
            self._check_file_for_patterns(
                yaml_file,
                "stdout_parsing",
                self.CODE_PATTERNS["stdout_parsing"]
            )
    
    def _scan_structural_issues(self):
        """Scan for structural anti-patterns"""
        # Check for package duplication
        package_definitions = defaultdict(list)
        
        for defaults_file in self.collection_path.rglob("defaults/main.yml"):
            try:
                with open(defaults_file) as f:
                    content = yaml.safe_load(f)
                    if not content:
                        continue
                    
                    # Look for package list variables
                    for key, value in content.items():
                        if "package" in key.lower() and isinstance(value, list):
                            role_name = defaults_file.parent.parent.name
                            for package in value:
                                if isinstance(package, str):
                                    package_definitions[package].append({
                                        "role": role_name,
                                        "file": str(defaults_file.relative_to(self.collection_path))
                                    })
            except Exception as e:
                pass
        
        # Report duplicated packages
        for package, locations in package_definitions.items():
            if len(locations) > 1:
                self.findings["package_duplication"].append({
                    "severity": "LOW",
                    "package": package,
                    "count": len(locations),
                    "locations": locations,
                    "description": f"Package '{package}' defined in {len(locations)} roles"
                })
    
    def _check_file_for_patterns(self, file_path: Path, pattern_type: str, pattern_config: Dict):
        """Check a file for specific patterns"""
        try:
            with open(file_path) as f:
                content = f.read()
                
                patterns = pattern_config.get("patterns", [])
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Get line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        self.findings[pattern_type].append({
                            "severity": pattern_config["severity"],
                            "file": str(file_path.relative_to(self.collection_path)),
                            "line": line_num,
                            "match": match.group(0),
                            "description": pattern_config["description"]
                        })
        except Exception:
            pass
    
    def generate_report(self, format: str = "text") -> str:
        """Generate anti-pattern detection report"""
        findings = self.scan()
        
        if format == "json":
            return json.dumps(findings, indent=2)
        
        # Text report
        lines = []
        lines.append("=" * 80)
        lines.append("ANSIBLE ANTI-PATTERN DETECTION REPORT")
        lines.append("=" * 80)
        
        # Count by severity
        severity_counts = defaultdict(int)
        for pattern_type, issues in findings.items():
            for issue in issues:
                severity_counts[issue["severity"]] += 1
        
        lines.append(f"\nFINDINGS SUMMARY:")
        lines.append(f"  CRITICAL: {severity_counts['CRITICAL']}")
        lines.append(f"  HIGH:     {severity_counts['HIGH']}")
        lines.append(f"  MEDIUM:   {severity_counts['MEDIUM']}")
        lines.append(f"  LOW:      {severity_counts['LOW']}")
        
        # Group by severity
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            severity_findings = []
            for pattern_type, issues in findings.items():
                for issue in issues:
                    if issue["severity"] == severity:
                        severity_findings.append((pattern_type, issue))
            
            if severity_findings:
                lines.append(f"\n{'=' * 80}")
                lines.append(f"{severity} SEVERITY ISSUES ({len(severity_findings)})")
                lines.append(f"{'=' * 80}")
                
                for pattern_type, issue in severity_findings:
                    lines.append(f"\n[{pattern_type}] {issue['description']}")
                    lines.append(f"  File: {issue['file']}")
                    if "line" in issue:
                        lines.append(f"  Line: {issue['line']}")
                    if "match" in issue:
                        lines.append(f"  Match: {issue['match']}")
                    if "lines" in issue:
                        lines.append(f"  Lines: {issue['lines']}")
                    if "count" in issue:
                        lines.append(f"  Occurrences: {issue['count']}")
                    if "locations" in issue:
                        for loc in issue["locations"][:5]:  # Show first 5
                            lines.append(f"    - {loc['role']}: {loc['file']}")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Detect anti-patterns in Ansible collections")
    parser.add_argument("collection_path", help="Path to Ansible collection root")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--severity", choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                        help="Minimum severity to report")
    
    args = parser.parse_args()
    
    try:
        detector = AntiPatternDetector(args.collection_path)
        report = detector.generate_report(format=args.format)
        
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
