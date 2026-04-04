#!/usr/bin/env python3
"""
GitAgent Migration Validator

This script validates the complete GitAgent migration of the syncopated-context repository.
It checks:
- agent.yaml registry structure and compliance
- All skills for proper GitAgent YAML frontmatter
- All tools for proper YAML structure and MCP compliance
- Generates comprehensive validation report

Usage: python3 validate-migration.py [--verbose] [--output=report.json]
"""

import argparse
import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ValidationIssue:
    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    category: str  # 'structure', 'syntax', 'compliance', 'missing'
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class SkillValidation:
    name: str
    path: str
    exists: bool
    valid_yaml: bool
    has_required_fields: bool
    issues: List[ValidationIssue]

    @property
    def is_valid(self) -> bool:
        return self.exists and self.valid_yaml and self.has_required_fields and not any(
            issue.severity in ['critical', 'high'] for issue in self.issues
        )


@dataclass
class ToolValidation:
    name: str
    path: str
    exists: bool
    valid_yaml: bool
    has_required_fields: bool
    mcp_compliant: bool
    issues: List[ValidationIssue]

    @property
    def is_valid(self) -> bool:
        return (self.exists and self.valid_yaml and self.has_required_fields
                and self.mcp_compliant and not any(
                    issue.severity in ['critical', 'high'] for issue in self.issues
                ))


@dataclass
class ValidationReport:
    timestamp: str
    agent_valid: bool
    skills_total: int
    skills_valid: int
    tools_total: int
    tools_valid: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    agent_issues: List[ValidationIssue]
    skill_validations: List[SkillValidation]
    tool_validations: List[ToolValidation]

    @property
    def overall_status(self) -> str:
        if self.critical_issues > 0:
            return "FAILED"
        elif self.high_issues > 0:
            return "WARNINGS"
        elif self.agent_valid and self.skills_valid == self.skills_total and self.tools_valid == self.tools_total:
            return "PASSED"
        else:
            return "INCOMPLETE"


class GitAgentValidator:
    def __init__(self, repo_path: str, verbose: bool = False):
        self.repo_path = Path(repo_path)
        self.verbose = verbose

        # GitAgent spec requirements
        self.required_agent_fields = ['spec_version', 'name', 'version', 'description']
        self.required_skill_fields = ['name', 'description', 'license', 'allowed-tools', 'metadata']
        self.required_tool_fields = ['name', 'description', 'version', 'input_schema']
        self.valid_licenses = ['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'proprietary']

    def log(self, message: str, level: str = "INFO"):
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{level}] {message}")

    def validate_yaml_file(self, file_path: Path) -> tuple[bool, Optional[dict], List[ValidationIssue]]:
        """Validate YAML file syntax and structure"""
        issues = []

        if not file_path.exists():
            issues.append(ValidationIssue(
                severity="critical",
                category="missing",
                message=f"File does not exist: {file_path}",
                location=str(file_path)
            ))
            return False, None, issues

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # For skill files, extract YAML frontmatter
            if file_path.name == 'SKILL.md':
                if not content.startswith('---'):
                    issues.append(ValidationIssue(
                        severity="critical",
                        category="structure",
                        message="Skill file missing YAML frontmatter",
                        location=str(file_path),
                        suggestion="Add YAML frontmatter starting with '---'"
                    ))
                    return False, None, issues

                # Extract frontmatter between --- markers
                parts = content.split('---', 2)
                if len(parts) < 3:
                    issues.append(ValidationIssue(
                        severity="critical",
                        category="structure",
                        message="Invalid YAML frontmatter structure",
                        location=str(file_path),
                        suggestion="Ensure frontmatter is enclosed in '---' markers"
                    ))
                    return False, None, issues

                yaml_content = parts[1].strip()
            else:
                yaml_content = content

            data = yaml.safe_load(yaml_content)

            if data is None:
                issues.append(ValidationIssue(
                    severity="high",
                    category="syntax",
                    message="YAML file is empty or contains only whitespace",
                    location=str(file_path)
                ))
                return False, None, issues

            return True, data, issues

        except yaml.YAMLError as e:
            issues.append(ValidationIssue(
                severity="critical",
                category="syntax",
                message=f"YAML syntax error: {str(e)}",
                location=str(file_path),
                suggestion="Fix YAML syntax errors"
            ))
            return False, None, issues
        except Exception as e:
            issues.append(ValidationIssue(
                severity="critical",
                category="structure",
                message=f"Error reading file: {str(e)}",
                location=str(file_path)
            ))
            return False, None, issues

    def validate_agent_yaml(self) -> tuple[bool, List[ValidationIssue]]:
        """Validate the main agent.yaml file"""
        issues = []
        agent_path = self.repo_path / "agent.yaml"

        self.log("Validating agent.yaml...")

        valid_yaml, data, yaml_issues = self.validate_yaml_file(agent_path)
        issues.extend(yaml_issues)

        if not valid_yaml:
            return False, issues

        # Check required fields
        missing_fields = []
        for field in self.required_agent_fields:
            if field not in data:
                missing_fields.append(field)

        if missing_fields:
            issues.append(ValidationIssue(
                severity="critical",
                category="compliance",
                message=f"Missing required fields: {', '.join(missing_fields)}",
                location="agent.yaml",
                suggestion=f"Add required fields: {missing_fields}"
            ))

        # Validate spec version
        if 'spec_version' in data:
            if data['spec_version'] != '0.1.0':
                issues.append(ValidationIssue(
                    severity="medium",
                    category="compliance",
                    message=f"Unexpected spec_version: {data['spec_version']}",
                    location="agent.yaml",
                    suggestion="Use spec_version: 0.1.0 for GitAgent compatibility"
                ))

        # Validate skills and tools are lists
        for field in ['skills', 'tools']:
            if field in data:
                if not isinstance(data[field], list):
                    issues.append(ValidationIssue(
                        severity="high",
                        category="structure",
                        message=f"{field} must be a list",
                        location="agent.yaml"
                    ))

        self.log(f"Agent validation: {len(issues)} issues found")
        return len([i for i in issues if i.severity in ['critical', 'high']]) == 0, issues

    def validate_skill(self, skill_name: str) -> SkillValidation:
        """Validate a single skill"""
        skill_path = self.repo_path / "skills" / skill_name / "SKILL.md"
        issues = []

        self.log(f"Validating skill: {skill_name}")

        valid_yaml, data, yaml_issues = self.validate_yaml_file(skill_path)
        issues.extend(yaml_issues)

        if not valid_yaml:
            return SkillValidation(
                name=skill_name,
                path=str(skill_path),
                exists=skill_path.exists(),
                valid_yaml=False,
                has_required_fields=False,
                issues=issues
            )

        # Check required fields
        missing_fields = []
        for field in self.required_skill_fields:
            if field not in data:
                missing_fields.append(field)

        if missing_fields:
            issues.append(ValidationIssue(
                severity="critical",
                category="compliance",
                message=f"Missing required fields: {', '.join(missing_fields)}",
                location=str(skill_path),
                suggestion=f"Add required fields: {missing_fields}"
            ))

        # Validate license
        if 'license' in data:
            if data['license'] not in self.valid_licenses:
                issues.append(ValidationIssue(
                    severity="medium",
                    category="compliance",
                    message=f"Unknown license: {data['license']}",
                    location=str(skill_path),
                    suggestion=f"Use one of: {', '.join(self.valid_licenses)}"
                ))

        # Validate description length
        if 'description' in data:
            if len(data['description']) > 1024:
                issues.append(ValidationIssue(
                    severity="high",
                    category="compliance",
                    message=f"Description too long: {len(data['description'])} chars (max 1024)",
                    location=str(skill_path),
                    suggestion="Shorten description to under 1024 characters"
                ))

        # Validate metadata structure
        if 'metadata' in data and isinstance(data['metadata'], dict):
            required_meta = ['author', 'version', 'category']
            missing_meta = [m for m in required_meta if m not in data['metadata']]
            if missing_meta:
                issues.append(ValidationIssue(
                    severity="medium",
                    category="compliance",
                    message=f"Missing metadata fields: {', '.join(missing_meta)}",
                    location=str(skill_path),
                    suggestion=f"Add metadata fields: {missing_meta}"
                ))

        return SkillValidation(
            name=skill_name,
            path=str(skill_path),
            exists=skill_path.exists(),
            valid_yaml=valid_yaml,
            has_required_fields=len(missing_fields) == 0,
            issues=issues
        )

    def validate_tool(self, tool_name: str) -> ToolValidation:
        """Validate a single tool"""
        tool_path = self.repo_path / "tools" / f"{tool_name}.yaml"
        issues = []

        self.log(f"Validating tool: {tool_name}")

        valid_yaml, data, yaml_issues = self.validate_yaml_file(tool_path)
        issues.extend(yaml_issues)

        if not valid_yaml:
            return ToolValidation(
                name=tool_name,
                path=str(tool_path),
                exists=tool_path.exists(),
                valid_yaml=False,
                has_required_fields=False,
                mcp_compliant=False,
                issues=issues
            )

        # Check required fields
        missing_fields = []
        for field in self.required_tool_fields:
            if field not in data:
                missing_fields.append(field)

        if missing_fields:
            issues.append(ValidationIssue(
                severity="critical",
                category="compliance",
                message=f"Missing required fields: {', '.join(missing_fields)}",
                location=str(tool_path),
                suggestion=f"Add required fields: {missing_fields}"
            ))

        # Validate MCP compliance (basic checks)
        mcp_compliant = True
        if 'input_schema' in data:
            schema = data['input_schema']
            if not isinstance(schema, dict):
                issues.append(ValidationIssue(
                    severity="high",
                    category="compliance",
                    message="input_schema must be an object",
                    location=str(tool_path)
                ))
                mcp_compliant = False
            elif 'type' not in schema:
                issues.append(ValidationIssue(
                    severity="medium",
                    category="compliance",
                    message="input_schema missing 'type' field",
                    location=str(tool_path),
                    suggestion="Add 'type' field to input_schema"
                ))

        return ToolValidation(
            name=tool_name,
            path=str(tool_path),
            exists=tool_path.exists(),
            valid_yaml=valid_yaml,
            has_required_fields=len(missing_fields) == 0,
            mcp_compliant=mcp_compliant,
            issues=issues
        )

    def run_validation(self) -> ValidationReport:
        """Run complete validation and return report"""
        print("🔍 Starting GitAgent Migration Validation...")
        print(f"Repository: {self.repo_path}")
        print("=" * 60)

        # Load agent.yaml to get skills and tools lists
        agent_path = self.repo_path / "agent.yaml"
        with open(agent_path, 'r') as f:
            agent_data = yaml.safe_load(f)

        skills = agent_data.get('skills', [])
        tools = agent_data.get('tools', [])

        print(f"📋 Found {len(skills)} skills and {len(tools)} tools to validate")
        print()

        # Validate agent.yaml
        agent_valid, agent_issues = self.validate_agent_yaml()

        # Validate all skills
        skill_validations = []
        for skill_name in skills:
            validation = self.validate_skill(skill_name)
            skill_validations.append(validation)

        # Validate all tools
        tool_validations = []
        for tool_name in tools:
            validation = self.validate_tool(tool_name)
            tool_validations.append(validation)

        # Collect issue statistics
        all_issues = agent_issues.copy()
        for sv in skill_validations:
            all_issues.extend(sv.issues)
        for tv in tool_validations:
            all_issues.extend(tv.issues)

        critical_count = len([i for i in all_issues if i.severity == 'critical'])
        high_count = len([i for i in all_issues if i.severity == 'high'])
        medium_count = len([i for i in all_issues if i.severity == 'medium'])
        low_count = len([i for i in all_issues if i.severity == 'low'])

        skills_valid = len([sv for sv in skill_validations if sv.is_valid])
        tools_valid = len([tv for tv in tool_validations if tv.is_valid])

        return ValidationReport(
            timestamp=datetime.now().isoformat(),
            agent_valid=agent_valid,
            skills_total=len(skills),
            skills_valid=skills_valid,
            tools_total=len(tools),
            tools_valid=tools_valid,
            critical_issues=critical_count,
            high_issues=high_count,
            medium_issues=medium_count,
            low_issues=low_count,
            agent_issues=agent_issues,
            skill_validations=skill_validations,
            tool_validations=tool_validations
        )


def print_validation_report(report: ValidationReport):
    """Print a human-readable validation report"""
    status_emoji = {
        "PASSED": "✅",
        "WARNINGS": "⚠️",
        "INCOMPLETE": "🔄",
        "FAILED": "❌"
    }

    print()
    print("=" * 60)
    print("🔍 GITAGENT MIGRATION VALIDATION REPORT")
    print("=" * 60)
    print(f"Timestamp: {report.timestamp}")
    print(f"Overall Status: {status_emoji.get(report.overall_status, '❓')} {report.overall_status}")
    print()

    print("📊 SUMMARY")
    print("-" * 30)
    print(f"Agent Registry:     {'✅ VALID' if report.agent_valid else '❌ INVALID'}")
    print(f"Skills:            {report.skills_valid}/{report.skills_total} valid")
    print(f"Tools:             {report.tools_valid}/{report.tools_total} valid")
    print()

    print("🚨 ISSUES BY SEVERITY")
    print("-" * 30)
    print(f"Critical:          {report.critical_issues}")
    print(f"High:              {report.high_issues}")
    print(f"Medium:            {report.medium_issues}")
    print(f"Low:               {report.low_issues}")
    print()

    # Show critical and high issues in detail
    if report.critical_issues > 0 or report.high_issues > 0:
        print("🔥 CRITICAL & HIGH PRIORITY ISSUES")
        print("-" * 50)

        all_issues = report.agent_issues.copy()
        for sv in report.skill_validations:
            all_issues.extend(sv.issues)
        for tv in report.tool_validations:
            all_issues.extend(tv.issues)

        critical_high = [i for i in all_issues if i.severity in ['critical', 'high']]
        for issue in critical_high[:10]:  # Show first 10
            severity_icon = "🔴" if issue.severity == "critical" else "🟠"
            print(f"{severity_icon} {issue.severity.upper()}: {issue.message}")
            if issue.location:
                print(f"   📍 {issue.location}")
            if issue.suggestion:
                print(f"   💡 {issue.suggestion}")
            print()

        if len(critical_high) > 10:
            print(f"... and {len(critical_high) - 10} more issues")
            print()

    # Show skill validation summary
    if report.skill_validations:
        print("📝 SKILLS VALIDATION")
        print("-" * 30)
        failed_skills = [sv for sv in report.skill_validations if not sv.is_valid]
        if failed_skills:
            print("❌ Failed Skills:")
            for sv in failed_skills:
                print(f"   • {sv.name} - {len(sv.issues)} issues")
        else:
            print("✅ All skills passed validation")
        print()

    # Show tool validation summary
    if report.tool_validations:
        print("🔧 TOOLS VALIDATION")
        print("-" * 30)
        failed_tools = [tv for tv in report.tool_validations if not tv.is_valid]
        if failed_tools:
            print("❌ Failed Tools:")
            for tv in failed_tools:
                print(f"   • {tv.name} - {len(tv.issues)} issues")
        else:
            print("✅ All tools passed validation")
        print()

    # Recommendations
    if report.overall_status == "FAILED":
        print("🚨 RECOMMENDATIONS")
        print("-" * 30)
        print("❌ Migration has CRITICAL issues that must be fixed before shipping")
        print("1. Fix all critical issues listed above")
        print("2. Re-run validation to confirm fixes")
        print("3. Address high priority issues")
    elif report.overall_status == "WARNINGS":
        print("⚠️  RECOMMENDATIONS")
        print("-" * 30)
        print("⚠️ Migration has warnings but may be shippable")
        print("1. Review high priority issues")
        print("2. Consider fixing before production deployment")
        print("3. Monitor for issues in testing")
    elif report.overall_status == "PASSED":
        print("✅ RECOMMENDATIONS")
        print("-" * 30)
        print("🎉 Migration validation PASSED!")
        print("✅ GitAgent migration is ready for testing")
        print("✅ All skills and tools meet GitAgent requirements")
        print("✅ Ready to proceed with export testing")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Validate GitAgent migration")
    parser.add_argument("--repo", default=".", help="Repository path (default: current directory)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--output", help="Output JSON report to file")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    try:
        validator = GitAgentValidator(args.repo, args.verbose)
        report = validator.run_validation()

        if args.format == "text":
            print_validation_report(report)
        else:
            # Convert dataclasses to dict for JSON serialization
            report_dict = asdict(report)
            print(json.dumps(report_dict, indent=2))

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(asdict(report), f, indent=2)
            print(f"\n📄 Report saved to: {args.output}")

        # Exit with appropriate code
        if report.overall_status == "FAILED":
            sys.exit(1)
        elif report.overall_status == "WARNINGS":
            sys.exit(2)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n❌ Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()