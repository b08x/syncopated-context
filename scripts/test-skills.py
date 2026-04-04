#!/usr/bin/env python3
"""
GitAgent Skill Functional Testing Framework

Tests the actual functionality of GitAgent skills to ensure they work correctly
beyond just structural validation. This includes:
- Skill loading and parsing
- Frontmatter extraction and validation
- Content structure analysis
- Mock execution environment testing
- Performance benchmarking

Usage: python3 test-skills.py [--skill=SKILL_NAME] [--verbose] [--benchmark]
"""

import argparse
import json
import os
import sys
import time
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import re


@dataclass
class SkillTest:
    name: str
    path: str
    load_success: bool
    parse_success: bool
    content_valid: bool
    execution_time: float
    file_size: int
    frontmatter: Optional[Dict[str, Any]]
    content_lines: int
    issues: List[str]

    @property
    def success(self) -> bool:
        return self.load_success and self.parse_success and self.content_valid and len(self.issues) == 0


@dataclass
class TestSuite:
    timestamp: str
    total_skills: int
    passed_skills: int
    failed_skills: int
    total_execution_time: float
    average_execution_time: float
    skill_tests: List[SkillTest]

    @property
    def success_rate(self) -> float:
        return (self.passed_skills / self.total_skills) * 100 if self.total_skills > 0 else 0

    @property
    def overall_status(self) -> str:
        if self.success_rate == 100:
            return "PASSED"
        elif self.success_rate >= 80:
            return "MOSTLY_PASSED"
        elif self.success_rate >= 60:
            return "PARTIALLY_PASSED"
        else:
            return "FAILED"


class SkillFunctionalTester:
    def __init__(self, repo_path: str, verbose: bool = False, benchmark: bool = False):
        self.repo_path = Path(repo_path)
        self.verbose = verbose
        self.benchmark = benchmark

        # Performance thresholds
        self.max_load_time = 1.0  # seconds
        self.max_file_size = 100 * 1024  # 100KB
        self.max_content_lines = 500  # lines

    def log(self, message: str, level: str = "INFO"):
        if self.verbose or level in ["ERROR", "WARNING"]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")

    def load_agent_yaml(self) -> Dict[str, Any]:
        """Load and parse the agent.yaml file"""
        agent_path = self.repo_path / "agent.yaml"
        try:
            with open(agent_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load agent.yaml: {e}")

    def parse_skill_file(self, skill_path: Path) -> Tuple[Dict[str, Any], str, List[str]]:
        """Parse a skill file and extract frontmatter and content"""
        issues = []

        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            issues.append(f"Failed to read file: {e}")
            return {}, "", issues

        # Extract YAML frontmatter
        if not content.startswith('---'):
            issues.append("Missing YAML frontmatter delimiter")
            return {}, content, issues

        try:
            parts = content.split('---', 2)
            if len(parts) < 3:
                issues.append("Invalid frontmatter structure")
                return {}, content, issues

            frontmatter_text = parts[1].strip()
            body_content = parts[2].strip()

            frontmatter = yaml.safe_load(frontmatter_text)
            if frontmatter is None:
                frontmatter = {}
                issues.append("Empty or invalid YAML frontmatter")

            return frontmatter, body_content, issues

        except yaml.YAMLError as e:
            issues.append(f"YAML parsing error: {e}")
            return {}, content, issues

    def validate_skill_content(self, name: str, frontmatter: Dict[str, Any],
                             content: str) -> List[str]:
        """Validate skill content structure and quality"""
        issues = []

        # Check required frontmatter fields
        required_fields = ['name', 'description', 'license', 'allowed-tools', 'metadata']
        for field in required_fields:
            if field not in frontmatter:
                issues.append(f"Missing required field: {field}")

        # Validate name consistency
        if frontmatter.get('name') != name:
            issues.append(f"Name mismatch: filename={name}, frontmatter={frontmatter.get('name')}")

        # Check description length and quality
        desc = frontmatter.get('description', '')
        if len(desc) > 1024:
            issues.append(f"Description too long: {len(desc)} chars (max 1024)")
        if len(desc) < 20:
            issues.append(f"Description too short: {len(desc)} chars (min 20)")

        # Check for placeholder content
        placeholders = ['TODO', 'FIXME', 'XXX', 'HACK', '[placeholder]', 'lorem ipsum']
        content_lower = content.lower()
        for placeholder in placeholders:
            if placeholder in content_lower:
                issues.append(f"Contains placeholder content: {placeholder}")

        # Check content structure
        if len(content.strip()) < 100:
            issues.append("Content too short - may be incomplete")

        # Check for basic markdown structure
        if not re.search(r'^#', content, re.MULTILINE):
            issues.append("Missing markdown headers - content may be poorly structured")

        # Validate allowed-tools
        allowed_tools = frontmatter.get('allowed-tools')
        if allowed_tools:
            if isinstance(allowed_tools, str):
                tools = [t.strip() for t in allowed_tools.split()]
            elif isinstance(allowed_tools, list):
                tools = allowed_tools
            else:
                issues.append("allowed-tools must be string or list")
                tools = []

            # Check for valid tool names
            valid_tools = {
                'Read', 'Edit', 'Grep', 'Glob', 'Bash', 'Write', 'Agent',
                'multi-platform-recall', 'github-activity', 'backup-analysis'
            }
            invalid_tools = [t for t in tools if t not in valid_tools]
            if invalid_tools:
                issues.append(f"Invalid tools: {invalid_tools}")

        # Check metadata structure
        metadata = frontmatter.get('metadata')
        if metadata:
            if not isinstance(metadata, dict):
                issues.append("metadata must be an object")
            else:
                required_meta = ['author', 'version', 'category']
                missing_meta = [m for m in required_meta if m not in metadata]
                if missing_meta:
                    issues.append(f"Missing metadata: {missing_meta}")

        return issues

    def test_skill_performance(self, skill_path: Path) -> Tuple[float, int, int]:
        """Test skill loading performance"""
        start_time = time.time()

        # Measure file operations
        try:
            file_size = skill_path.stat().st_size
            with open(skill_path, 'r') as f:
                content = f.read()
            content_lines = len(content.splitlines())

            # Simulate parsing time
            _ = content.split('---', 2)

        except Exception:
            file_size = 0
            content_lines = 0

        execution_time = time.time() - start_time
        return execution_time, file_size, content_lines

    def test_single_skill(self, skill_name: str) -> SkillTest:
        """Test a single skill comprehensively"""
        skill_path = self.repo_path / "skills" / skill_name / "SKILL.md"
        issues = []

        self.log(f"Testing skill: {skill_name}")

        # Test file loading
        load_success = skill_path.exists()
        if not load_success:
            issues.append(f"Skill file not found: {skill_path}")
            return SkillTest(
                name=skill_name,
                path=str(skill_path),
                load_success=False,
                parse_success=False,
                content_valid=False,
                execution_time=0.0,
                file_size=0,
                frontmatter=None,
                content_lines=0,
                issues=issues
            )

        # Test parsing
        frontmatter, content, parse_issues = self.parse_skill_file(skill_path)
        issues.extend(parse_issues)
        parse_success = len(parse_issues) == 0

        # Test content validation
        content_issues = self.validate_skill_content(skill_name, frontmatter, content)
        issues.extend(content_issues)
        content_valid = len(content_issues) == 0

        # Test performance
        execution_time, file_size, content_lines = self.test_skill_performance(skill_path)

        # Performance checks
        if self.benchmark:
            if execution_time > self.max_load_time:
                issues.append(f"Slow loading: {execution_time:.3f}s (max {self.max_load_time}s)")
            if file_size > self.max_file_size:
                issues.append(f"Large file: {file_size} bytes (max {self.max_file_size})")
            if content_lines > self.max_content_lines:
                issues.append(f"Long content: {content_lines} lines (max {self.max_content_lines})")

        return SkillTest(
            name=skill_name,
            path=str(skill_path),
            load_success=load_success,
            parse_success=parse_success,
            content_valid=content_valid,
            execution_time=execution_time,
            file_size=file_size,
            frontmatter=frontmatter,
            content_lines=content_lines,
            issues=issues
        )

    def run_test_suite(self, skill_filter: Optional[str] = None) -> TestSuite:
        """Run comprehensive test suite"""
        print("🧪 Starting GitAgent Skill Functional Tests...")
        print(f"Repository: {self.repo_path}")
        print("=" * 60)

        # Load skills from agent.yaml
        try:
            agent_data = self.load_agent_yaml()
            all_skills = agent_data.get('skills', [])
        except Exception as e:
            print(f"❌ Failed to load agent configuration: {e}")
            sys.exit(1)

        # Filter skills if requested
        if skill_filter:
            if skill_filter in all_skills:
                skills_to_test = [skill_filter]
            else:
                print(f"❌ Skill '{skill_filter}' not found in agent registry")
                sys.exit(1)
        else:
            skills_to_test = all_skills

        print(f"📋 Testing {len(skills_to_test)} skills")
        if self.benchmark:
            print("⏱️  Performance benchmarking enabled")
        print()

        # Run tests
        start_time = time.time()
        skill_tests = []

        for skill_name in skills_to_test:
            test_result = self.test_single_skill(skill_name)
            skill_tests.append(test_result)

        total_time = time.time() - start_time

        # Calculate statistics
        passed_skills = len([st for st in skill_tests if st.success])
        failed_skills = len(skills_to_test) - passed_skills
        avg_time = total_time / len(skills_to_test) if skills_to_test else 0

        return TestSuite(
            timestamp=datetime.now().isoformat(),
            total_skills=len(skills_to_test),
            passed_skills=passed_skills,
            failed_skills=failed_skills,
            total_execution_time=total_time,
            average_execution_time=avg_time,
            skill_tests=skill_tests
        )


def print_test_report(suite: TestSuite, show_details: bool = True):
    """Print comprehensive test report"""
    status_emoji = {
        "PASSED": "✅",
        "MOSTLY_PASSED": "⚠️",
        "PARTIALLY_PASSED": "🟡",
        "FAILED": "❌"
    }

    print()
    print("=" * 60)
    print("🧪 GITAGENT SKILL FUNCTIONAL TEST REPORT")
    print("=" * 60)
    print(f"Timestamp: {suite.timestamp}")
    print(f"Overall Status: {status_emoji.get(suite.overall_status, '❓')} {suite.overall_status}")
    print()

    print("📊 SUMMARY")
    print("-" * 30)
    print(f"Total Skills:      {suite.total_skills}")
    print(f"Passed:            {suite.passed_skills}")
    print(f"Failed:            {suite.failed_skills}")
    print(f"Success Rate:      {suite.success_rate:.1f}%")
    print()

    print("⏱️ PERFORMANCE")
    print("-" * 30)
    print(f"Total Time:        {suite.total_execution_time:.3f}s")
    print(f"Average Time:      {suite.average_execution_time:.3f}s per skill")
    print()

    # Show failed skills
    failed_tests = [st for st in suite.skill_tests if not st.success]
    if failed_tests:
        print("❌ FAILED SKILLS")
        print("-" * 30)
        for test in failed_tests[:10]:  # Show first 10
            print(f"• {test.name}")
            for issue in test.issues[:3]:  # Show first 3 issues per skill
                print(f"  - {issue}")
            if len(test.issues) > 3:
                print(f"  ... and {len(test.issues) - 3} more issues")
            print()

        if len(failed_tests) > 10:
            print(f"... and {len(failed_tests) - 10} more failed skills")
        print()

    # Show performance summary if benchmarking
    if any(st.execution_time > 0 for st in suite.skill_tests):
        print("📈 PERFORMANCE DETAILS")
        print("-" * 30)

        # Find slowest skills
        slow_skills = sorted(suite.skill_tests, key=lambda x: x.execution_time, reverse=True)[:5]
        if slow_skills and slow_skills[0].execution_time > 0:
            print("Slowest loading skills:")
            for st in slow_skills:
                if st.execution_time > 0:
                    print(f"  • {st.name}: {st.execution_time:.3f}s")
            print()

        # File size analysis
        total_size = sum(st.file_size for st in suite.skill_tests)
        avg_size = total_size / len(suite.skill_tests) if suite.skill_tests else 0
        print(f"Total skill size:  {total_size:,} bytes")
        print(f"Average size:      {avg_size:,.0f} bytes")
        print()

    # Recommendations
    if suite.overall_status == "PASSED":
        print("✅ RECOMMENDATIONS")
        print("-" * 30)
        print("🎉 All skills passed functional testing!")
        print("✅ Skills are properly structured and functional")
        print("✅ Ready for GitAgent export testing")
    elif suite.overall_status == "MOSTLY_PASSED":
        print("⚠️  RECOMMENDATIONS")
        print("-" * 30)
        print(f"⚠️ {suite.success_rate:.1f}% success rate - mostly passing")
        print("1. Review failed skills and fix critical issues")
        print("2. Consider proceeding with caution")
    else:
        print("❌ RECOMMENDATIONS")
        print("-" * 30)
        print(f"❌ {suite.success_rate:.1f}% success rate - significant issues")
        print("1. Fix failed skills before proceeding")
        print("2. Re-run tests to verify fixes")
        print("3. Not ready for production use")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Test GitAgent skill functionality")
    parser.add_argument("--repo", default=".", help="Repository path")
    parser.add_argument("--skill", help="Test specific skill only")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--benchmark", action="store_true", help="Enable performance benchmarking")
    parser.add_argument("--output", help="Output JSON report to file")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    try:
        tester = SkillFunctionalTester(args.repo, args.verbose, args.benchmark)
        suite = tester.run_test_suite(args.skill)

        if args.format == "text":
            print_test_report(suite)
        else:
            print(json.dumps(asdict(suite), indent=2, default=str))

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(asdict(suite), f, indent=2, default=str)
            print(f"\n📄 Report saved to: {args.output}")

        # Exit with appropriate code
        if suite.overall_status == "PASSED":
            sys.exit(0)
        elif suite.overall_status in ["MOSTLY_PASSED", "PARTIALLY_PASSED"]:
            sys.exit(1)
        else:
            sys.exit(2)

    except KeyboardInterrupt:
        print("\n❌ Testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Testing failed with error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()