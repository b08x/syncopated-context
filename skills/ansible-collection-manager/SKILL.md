---
name: ansible-collection-manager
description: Comprehensive toolkit for analyzing, managing, and refactoring Ansible collections. Detects anti-patterns, analyzes dependencies, traces variable precedence.
license: MIT
allowed-tools: Read Edit Grep Glob Bash Write
metadata:
  author: b08x
  version: "1.0.0"
  category: automation
---

# Ansible Collection Manager (v1)

GenAI interface for managing Ansible collections through static analysis, dependency mapping, and refactoring workflows. This v1 skill uses Python-based analysis tools with native Ansible CLI integration. Future v2 will integrate with Ruby graph ontology stack (FalkorDB, pgvector, ruby_llm).

## When to Use This Skill

Trigger this skill when users ask about:

**Understanding & Mapping:**
- Analyze collection structure and complexity
- Map role dependencies and call graphs  
- Identify complexity hotspots
- Generate dependency visualizations

**Security & Anti-Pattern Detection:**
- Find security vulnerabilities
- Scan for unencrypted secrets
- Detect deprecated protocols (SMB1/NTLMv1)
- Identify code smells and anti-patterns

**Refactoring & Consolidation:**
- Find package duplication across roles
- Consolidate packages into common vars
- Identify monolithic files needing splits
- Detect misplaced templates

**Variable Analysis:**
- Trace variable precedence chains
- Find shadowed variables
- Locate variable definitions and usage
- Identify secrets

**Code Quality:**
- Find orphaned roles
- Detect circular dependencies
- Locate large files for refactoring
- Find tasks missing idempotency controls

## Core Analysis Tools

All tools are exposed via **Model Context Protocol (MCP)** for use with GenAI CLI applications (claude-code, gemini-cli, antigravity, opencode). Each tool can also be run directly as a Python script.

### MCP Server

**Script:** `scripts/mcp_server.py`

The MCP server exposes all analysis tools via JSON-RPC over stdio. Configure in your CLI tool's MCP settings.

**Configuration:** See `references/mcp-configuration.md` for setup instructions.

### Tool 1: Collection Analyzer

**MCP Tool Name:** `ansible_analyze_collection`
**Script:** `scripts/collection_analyzer.py`

Provides comprehensive structural analysis and complexity metrics.

**MCP Usage (automatic via CLI):**
```
"Analyze the structure of my collection at ~/ansible-rhel-workstation-builder"
```

**Direct Script Usage:**
```bash
python scripts/collection_analyzer.py /path/to/collection
python scripts/collection_analyzer.py /path/to/collection --format json
python scripts/collection_analyzer.py /path/to/collection --output report.txt
```

**Analyzes:**
- Collection structure (galaxy.yml, ansible.cfg)
- Role inventory with file counts
- Playbook analysis
- Plugin types
- Complexity metrics (files, lines, depth, large files)
- Per-role complexity

**Use for:** Initial assessment, understanding scale, identifying hotspots.

### Tool 2: Anti-Pattern Detector

**MCP Tool Name:** `ansible_detect_antipatterns`
**Script:** `scripts/antipattern_detector.py`

Identifies security issues, anti-patterns, and code smells with severity ratings.

**MCP Usage (automatic via CLI):**
```
"Find critical security issues in my collection"
"Scan for unencrypted secrets and SMB1 usage"
```

**Direct Script Usage:**
```bash
python scripts/antipattern_detector.py /path/to/collection
python scripts/antipattern_detector.py /path/to/collection --format json
python scripts/antipattern_detector.py /path/to/collection --severity CRITICAL
```

**Detects:**
- CRITICAL: Unencrypted secrets, empty passwords, SMB1/NTLMv1
- HIGH: Root-equivalent privileges, sudo without password
- MEDIUM: Templates in files/, shell without validation, monolithic defaults
- LOW: Hardcoded timeouts, package duplication

**Use for:** Security audits, pre-deployment checks, code quality reviews.

### Tool 3: Package Consolidator

**MCP Tool Name:** `ansible_consolidate_packages`
**Script:** `scripts/package_consolidator.py`

Identifies package duplication and generates consolidation plans.

**MCP Usage (automatic via CLI):**
```
"Help me consolidate packages - create a plan"
"Find package duplication across roles"
```

**Direct Script Usage:**
```bash
python scripts/package_consolidator.py /path/to/collection
python scripts/package_consolidator.py /path/to/collection --plan
python scripts/package_consolidator.py /path/to/collection --format json
```

**Analyzes:**
- Package definitions across roles
- Duplication levels (highly/moderately/slightly duplicated)
- Generates consolidation recommendations
- Creates per-role cleanup actions

**Use for:** Planning package refactoring, reducing maintenance, ensuring consistency.

### Tool 4: Variable Analyzer

**MCP Tool Name:** `ansible_analyze_variables`
**Script:** `scripts/variable_analyzer.py`

Traces variable precedence, detects shadowing, finds usage.

**MCP Usage (automatic via CLI):**
```
"Trace precedence for db_password variable"
"Find all shadowed variables"
```

**Direct Script Usage:**
```bash
python scripts/variable_analyzer.py /path/to/collection
python scripts/variable_analyzer.py /path/to/collection --shadowed-only
python scripts/variable_analyzer.py /path/to/collection --variable db_password
```

**Analyzes:**
- Variable definitions across all precedence levels
- Shadowing detection
- Secret variable identification
- Variable usage in tasks

**Use for:** Understanding precedence, debugging config, finding shadowed variables.

### Tool 5: Role Dependency Mapper

**MCP Tool Name:** `ansible_map_dependencies`
**Script:** `scripts/role_mapper.py`

Maps role dependencies, generates call graphs, detects issues.

**MCP Usage (automatic via CLI):**
```
"Show role dependencies and generate Mermaid graph"
"Find circular dependencies"
```

**Direct Script Usage:**
```bash
python scripts/role_mapper.py /path/to/collection
python scripts/role_mapper.py /path/to/collection --graph
python scripts/role_mapper.py /path/to/collection --format mermaid
```

**Analyzes:**
- Role dependencies from meta/main.yml
- Playbook role inclusions
- Circular dependencies
- Orphaned roles
- Dependency depth

**Use for:** Understanding relationships, blast radius analysis, architecture diagrams.

## MCP Server Setup

To use these tools with GenAI CLI applications (claude-code, gemini-cli, antigravity, opencode/oh-my-opencode):

### 1. Configure MCP Server

Add to your CLI tool's MCP configuration file:

**Claude Code** (`~/.config/claude-code/mcp_servers.json`):
```json
{
  "mcpServers": {
    "ansible-collection-manager": {
      "command": "python3",
      "args": ["/path/to/ansible-collection-manager/scripts/mcp_server.py"],
      "transport": "stdio"
    }
  }
}
```

**Gemini CLI** (`~/.config/gemini-cli/mcp_servers.json`):
```json
{
  "servers": {
    "ansible-collection-manager": {
      "command": "python3",
      "args": ["/path/to/ansible-collection-manager/scripts/mcp_server.py"],
      "protocol": "stdio"
    }
  }
}
```

See `references/mcp-configuration.md` for complete configuration examples for all CLI tools.

### 2. Verify Setup

Test the MCP server:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python3 scripts/mcp_server.py
```

Should return tool definitions for all 5 tools.

### 3. Use in CLI

Once configured, simply ask natural questions:
```
"Analyze my ansible-rhel-workstation-builder collection"
"Find security vulnerabilities"
"Help me consolidate packages"
```

The CLI tool automatically invokes the appropriate MCP tools.

## Common Workflows

### Workflow 1: Initial Collection Assessment

User wants to understand their collection.

**Steps:**
1. Run collection_analyzer.py for structure overview
2. Present key metrics (files, roles, complexity)
3. Run role_mapper.py --graph for visual architecture
4. Run antipattern_detector.py for health check
5. Summarize with specific recommendations

**Example:**
```
User: "Analyze my ansible-rhel-workstation-builder collection"

Action sequence:
1. python scripts/collection_analyzer.py /path/to/collection
2. Present: 476 files, 16 roles, 8249 YAML lines, depth 9
3. Highlight: 20 large files (>100 lines) - refactoring candidates
4. python scripts/role_mapper.py /path/to/collection --graph
5. Quick security scan with antipattern_detector.py
6. Provide summary with actionable insights
```

### Workflow 2: Security Audit

User wants to find security vulnerabilities.

**Steps:**
1. Run antipattern_detector.py
2. Filter CRITICAL and HIGH severity
3. For each finding: show location, explain risk, suggest fix
4. Check secrets with variable_analyzer.py
5. Generate prioritized action plan

**Example:**
```
User: "Find security issues in my NAS role"

Action sequence:
1. python scripts/antipattern_detector.py /path/to/collection
2. Filter findings in roles/nas/
3. Present by severity:
   CRITICAL: SMB1 enabled in nas/defaults/main.yml:239
   → Risk: Vulnerable to known exploits
   → Fix: Set min_protocol: SMB2
4. Check for secrets in nas vars
5. Generate action plan with code examples
```

### Workflow 3: Package Consolidation

User wants to consolidate duplicated packages.

**Steps:**
1. Run package_consolidator.py --plan
2. Review highly duplicated packages (5+ roles)
3. Generate common/vars/packages.yml content
4. Create per-role cleanup instructions
5. Generate migration steps

**Example:**
```
User: "Help me consolidate packages - firewalld appears in 8 roles"

Action sequence:
1. python scripts/package_consolidator.py /path/to/collection --plan
2. Identify: firewalld, policycoreutils in 8 roles each
3. Generate common/vars/packages.yml:
   ---
   common_system_packages:
     - firewalld
     - policycoreutils
4. Create cleanup plan for each role
5. Provide migration steps with test commands
```

### Workflow 4: Dependency Analysis

User wants to understand role dependencies.

**Steps:**
1. Run role_mapper.py
2. Check for circular dependencies
3. Identify orphaned roles
4. Generate dependency graph (Mermaid)
5. Calculate blast radius

**Example:**
```
User: "What's the blast radius of refactoring the common role?"

Action sequence:
1. python scripts/role_mapper.py /path/to/collection
2. Find common role dependencies
3. Show "depended_by": workstation, nas, audio, rpm-dev (8 total)
4. Calculate downstream impacts
5. Generate Mermaid graph
6. Present: "Common role affects 8 roles, 3 playbooks, depth 2"
```

### Workflow 5: Variable Tracing

User wants to understand variable precedence.

**Steps:**
1. Run variable_analyzer.py --variable <name>
2. Show all definitions with precedence
3. Identify shadowing
4. Show usage locations
5. Explain which value wins

**Example:**
```
User: "Where is db_password defined and is it being shadowed?"

Action sequence:
1. python scripts/variable_analyzer.py /path/to/collection --variable db_password
2. Show definitions:
   - role_defaults (precedence 1): roles/app/defaults/main.yml
   - role_vars (precedence 4): roles/app/vars/main.yml  
3. Flag: ⚠️ SHADOWING DETECTED
4. Show winning definition: role_vars
5. List usage in tasks
6. Recommend keeping only highest precedence
```

## Integration with Native Ansible Tools

Complement analysis with native tools:

**ansible-lint:** Catch common mistakes
```bash
ansible-lint  # Integrate findings with antipattern_detector.py
```

**ansible-inventory:** Get actual inventory data
```bash
ansible-inventory --list --export  # Use with variable_analyzer.py
```

**ansible-doc:** Module documentation
```bash
ansible-doc <module>  # Reference for task analysis
```

**ansible-navigator:** Structured execution output
```bash
ansible-navigator run playbook.yml --mode stdout --format json
```

**ansible-galaxy:** Dependency management
```bash
ansible-galaxy collection list  # Integrate with collection_analyzer.py
```

## Best Practices

1. **Start with collection root:** All scripts expect collection root directory path

2. **Begin with collection_analyzer.py:** Get overview before detailed analysis

3. **Prioritize security:** Address CRITICAL/HIGH severity first

4. **Validate refactoring:** Use `--check --diff` before applying changes

5. **Combine tools:** Run multiple scripts for comprehensive analysis
   ```bash
   collection_analyzer.py . > overview.txt
   antipattern_detector.py . > security.txt
   role_mapper.py . --graph > dependencies.txt
   package_consolidator.py . --plan > consolidation.txt
   ```

6. **Generate files when requested:** Create actual YAML/code if user asks

7. **Use Mermaid for visualization:** Generate graphs for dependency relationships

8. **Respect conventions:** Maintain collection's existing style (indentation, etc.)

## Reference Materials

See `references/ansible-architecture.md` for:
- Collection-first architecture principles
- Variable precedence rules
- Anti-pattern catalog with examples
- Execution Environment concepts
- Refactoring strategies
- Graph ontology concepts (for v2)

## Example Interactions

### Example: Quick Security Audit

**User:** "Scan my collection for security issues"

**Response Strategy:**
1. Call antipattern_detector.py
2. Group by severity
3. Present CRITICAL first:
   ```
   🔴 CRITICAL ISSUES FOUND:
   
   1. Unencrypted Secrets
      File: vars/secrets.yml:12
      Match: gmail_password:
      → Use: ansible-vault encrypt vars/secrets.yml
   
   2. Empty Password
      File: roles/kiwi/defaults/main.yml:45
      Match: kiwi_root_password: ""
      → Set strong password or document test-only use
   ```
4. Continue with HIGH, MEDIUM, LOW
5. Generate prioritized action plan

### Example: Package Consolidation

**User:** "Help me consolidate packages - they're duplicated across 12 roles"

**Response Strategy:**
1. Call package_consolidator.py --plan
2. Show highly duplicated:
   ```
   HIGHLY DUPLICATED (5+ roles):
   firewalld (8 roles): audio, nas, workstation, common, ...
   policycoreutils (8 roles): audio, nas, workstation, ...
   ```
3. Generate common/vars/packages.yml:
   ```yaml
   ---
   common_system_packages:
     - firewalld
     - policycoreutils
   ```
4. Show per-role cleanup
5. Create migration guide

### Example: Dependency Mapping

**User:** "Map my role dependencies and show circular dependencies"

**Response Strategy:**
1. Call role_mapper.py --graph
2. Check for cycles
3. If found:
   ```
   ⚠️ CIRCULAR DEPENDENCY DETECTED:
   Cycle: workstation → audio → base → workstation
   ```
4. Generate Mermaid graph
5. Explain impact and resolution

## Limitations (v1)

This v1 uses **static analysis only**. Not included:

- Live graph database queries (FalkorDB)
- Semantic search (pgvector)  
- LLM-powered refactoring (ruby_llm)
- MCP server integration
- Real-time inventory from running systems
- Dynamic variable resolution from execution

These will be available in v2 with Ruby graph ontology stack.

## Future: v2 Graph Ontology Integration

When Ruby stack is ready, v2 will enable:

- **Semantic queries:** "Find roles related to nginx hardening"
- **Graph traversal:** "All variables consumed by this task"
- **AI refactoring:** "Suggest optimal package consolidation"
- **Dependency reasoning:** "What breaks if I update this module?"
- **Autonomous management:** "Self-healing automation"

The v1 scripts generate data compatible with future graph ingestion.

## Technical Notes

**MCP Architecture:**
- Tools exposed via Model Context Protocol (JSON-RPC over stdio)
- Compatible with claude-code, gemini-cli, antigravity, opencode
- 5-minute timeout per tool execution
- Automatic tool selection by CLI based on user intent

**Direct Script Usage:**
- All scripts support `--format json` for programmatic use
- Scripts are idempotent and safe (read-only analysis)
- Error handling with informative messages
- Works with any Ansible collection structure
- Extensible with custom pattern detection rules
- Python 3.9+ required, uses standard library + PyYAML

**Dual Access:**
- **MCP tools:** Best for interactive CLI use (natural language)
- **Direct scripts:** Best for CI/CD, automation, scripting
- Both modes use identical analysis logic
