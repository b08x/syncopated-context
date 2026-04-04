# Ansible Collection Architecture Reference

## Collection-First Architecture (2025-2026 Best Practices)

### Core Principles

Modern Ansible follows a **collection-first** approach where Collections are the primary unit of content delivery, replacing standalone roles scattered across repositories.

**Key Benefits:**
- **Namespace isolation**: FQCN (Fully Qualified Collection Names) eliminate ambiguity
- **Versioned artifacts**: Collections package roles, modules, plugins as single units
- **Dependency management**: Clear dependency graphs via `galaxy.yml`
- **Execution Environments**: Containerized runtimes with bundled dependencies

### Standard Collection Structure

```
collection_namespace.collection_name/
├── galaxy.yml                 # Metadata: version, dependencies, namespace
├── roles/                     # Modular automation units
│   ├── role_name/
│   │   ├── tasks/            # Main automation logic
│   │   ├── defaults/         # Default variables (lowest precedence)
│   │   ├── vars/             # Role variables (high precedence)
│   │   ├── handlers/         # Event handlers
│   │   ├── templates/        # Jinja2 templates
│   │   ├── files/            # Static files
│   │   └── meta/
│   │       └── main.yml      # Role dependencies, min_ansible_version
├── plugins/                   # Python extensions
│   ├── modules/              # Custom modules
│   ├── filters/              # Jinja2 filters
│   └── callbacks/            # Callback plugins
├── playbooks/                 # High-level orchestration
├── meta/
│   └── execution-environment.yml  # EE build requirements
└── tests/                     # Integration tests
```

### Variable Precedence (Simplified)

From lowest to highest precedence:
1. **role defaults** (`defaults/main.yml`) - Baseline values
2. **inventory group_vars** - Group-level overrides
3. **inventory host_vars** - Host-specific values
4. **role vars** (`vars/main.yml`) - Role-specific configuration
5. **play vars** - Playbook-level variables
6. **extra vars** (`-e` on command line) - Highest precedence

**Shadowing** occurs when the same variable is defined at multiple precedence levels. The higher precedence wins, but this can cause confusion.

## Anti-Patterns to Avoid

### Security Anti-Patterns (CRITICAL)

1. **Unencrypted Secrets**
   - Problem: Storing passwords, tokens, API keys in plain text
   - Solution: Use Ansible Vault for `vars/secrets.yml`
   ```bash
   ansible-vault encrypt vars/secrets.yml
   ```

2. **SMB1/NTLMv1 Protocols**
   - Problem: Using deprecated, insecure protocols
   - Solution: Set `min_protocol: SMB2` or higher
   
3. **Empty/Default Passwords**
   - Problem: Live ISOs or test configs with blank passwords
   - Solution: Always set strong passwords, document test credentials

4. **Shell Commands Without Validation**
   - Problem: Using `ansible.builtin.shell` without input sanitization
   - Solution: Use structured modules when possible, validate inputs

5. **Root-Equivalent Privileges**
   - Problem: Adding users to docker/libvirt groups grants root-level access
   - Solution: Document security implications, use least privilege

### Structural Anti-Patterns

1. **Templates in files/ Directory**
   - Problem: Jinja2 templates placed in `files/` instead of `templates/`
   - Impact: Confusing organization, harder to maintain
   - Solution: Move `.j2` files to `templates/`

2. **Monolithic Defaults Files**
   - Problem: Single `defaults/main.yml` with 200+ lines
   - Impact: Hard to maintain, find variables
   - Solution: Split into logical files:
     - `defaults/packages.yml`
     - `defaults/config.yml`
     - `defaults/build_settings.yml`

3. **Package Duplication**
   - Problem: Common packages (firewalld, policycoreutils) repeated across roles
   - Impact: Maintenance overhead, inconsistent versions
   - Solution: Consolidate into `common/vars/packages.yml`

4. **Stdout Parsing**
   - Problem: Using regex on command stdout instead of structured output
   - Impact: Brittle, error-prone
   - Solution: Use JSON output modes (`ansible-navigator --format json`)

5. **Hardcoded Values**
   - Problem: Timeout values, paths hardcoded in tasks
   - Impact: Inflexible, requires code changes
   - Solution: Extract to variables with sensible defaults

6. **Missing `changed_when` on Shell/Command**
   - Problem: Idempotency broken, always reports "changed"
   - Impact: Can't track real changes
   - Solution: Add `changed_when` clauses

## Dependency Graph Concepts

### Node Types in Ansible Architecture

Understanding these relationships enables deep reasoning about infrastructure:

- **Collection**: Top-level namespace container
- **Role**: Modular automation unit
- **Playbook**: High-level orchestration workflow
- **Play**: Execution unit targeting specific hosts
- **Task**: Atomic operation (module invocation)
- **Variable**: Configuration data
- **Module**: Ansible's interface to system operations
- **InventoryGroup**: Logical host grouping
- **Host**: Physical/virtual target

### Relationship Types (Edges)

1. **Structural Composition**
   - `Collection → COMPOSED_OF → Role`
   - `Playbook → COMPOSED_OF → Play`
   - `Play → COMPOSED_OF → Task`

2. **Dependencies & Flow**
   - `Play → CALLS → Role` (runtime invocation)
   - `Role → DEPENDS_ON → Role` (meta/main.yml dependencies)
   - `Task → USES → Module` (module invocation)

3. **Data Flow**
   - `Role → DEFINES → Variable`
   - `Task → USES → Variable` (Jinja2 references)

4. **Control Structures**
   - `Task → ITERATES_OVER → Variable` (loops)
   - `Task → GOVERNED_BY → Variable` (conditionals)

### Analysis Capabilities

With mapped dependencies, you can:
- **Blast radius analysis**: "Which roles are impacted by refactoring common?"
- **Circular dependency detection**: Prevent infinite loops
- **Orphaned code identification**: Find unused roles/tasks
- **Variable shadowing detection**: Identify precedence conflicts
- **Impact analysis**: "What breaks if I deprecate this module?"

## Execution Environments (EEs)

### Purpose

EEs solve "dependency hell" by containerizing:
1. Ansible Core
2. Collections
3. Python libraries (boto3, requests)
4. System packages (git, openssh)

### Why EEs Matter for AI Agents

Without EEs, AI-generated playbooks may:
- Assume libraries that don't exist
- Fail with cryptic import errors
- Create "hallucination loops" trying to fix code instead of environment

### EE Definition

`meta/execution-environment.yml`:
```yaml
---
version: 3
dependencies:
  galaxy: requirements.yml
  python: requirements.txt
  system: bindep.txt
```

### Best Practices

- **Always use ansible-navigator** for execution (not raw `ansible-playbook`)
- Define EE requirements at collection level
- Test in containers to ensure reproducibility

## Ansible Navigator

### Machine-Readable Output

Traditional Ansible outputs colorful text. Navigator provides structured JSON:

```bash
ansible-navigator run playbook.yml --mode stdout --format json
```

Returns:
```json
{
  "plays": [...],
  "stats": {
    "failures": {},
    "ok": {},
    "changed": {}
  }
}
```

### Benefits for Automation

- Parse execution results programmatically
- Distinguish syntax errors vs. connection failures vs. logic errors
- Enable AI agents to diagnose issues with precision
- Support CI/CD integration

## Refactoring Strategies

### Package Consolidation

**Before:**
```
roles/audio/defaults/main.yml: firewalld, policycoreutils
roles/nas/defaults/main.yml: firewalld, policycoreutils
roles/workstation/defaults/main.yml: firewalld, policycoreutils
```

**After:**
```yaml
# roles/common/vars/packages.yml
common_packages:
  - firewalld
  - policycoreutils
  - ...
```

**Migration:**
1. Identify duplicated packages (use package_consolidator.py)
2. Create `common/vars/packages.yml`
3. Update roles to import from common
4. Remove duplicates from role defaults
5. Test with `--check --diff`

### Flattening Monolithic Defaults

**Before:**
```yaml
# roles/kiwi/defaults/main.yml (273 lines)
kiwi_packages: [...]
kiwi_build_timeout: 7200
kiwi_nvidia_enabled: true
kiwi_oneapi_enabled: false
# ... 200+ more lines
```

**After:**
```yaml
# roles/kiwi/defaults/packages.yml
kiwi_packages: [...]

# roles/kiwi/defaults/build.yml
kiwi_build_timeout: 7200
kiwi_async_poll: 0

# roles/kiwi/defaults/features.yml
kiwi_nvidia_enabled: true
kiwi_oneapi_enabled: false
```

### Moving Templates from files/

**Incorrect:**
```
roles/rpm-dev/files/etc/mock/templates/fedora-43.cfg.j2
```

**Correct:**
```
roles/rpm-dev/templates/mock/fedora-43.cfg.j2
```

Then update tasks:
```yaml
# Before
- name: Deploy Mock config
  copy:
    src: etc/mock/templates/fedora-43.cfg.j2
    dest: /etc/mock/fedora-43.cfg

# After
- name: Deploy Mock config
  template:
    src: mock/fedora-43.cfg.j2
    dest: /etc/mock/fedora-43.cfg
```

## Testing & Validation

### Linting

```bash
# Ansible Lint - catch common mistakes
ansible-lint

# YAML Lint - enforce formatting
yamllint -c .yamllint.yaml .

# Custom rules in .ansible-lint
```

### Dry Run

```bash
# Preview changes without applying
ansible-playbook playbook.yml --check --diff
```

### Molecule (Advanced)

For proper testing infrastructure:
```bash
molecule init scenario
molecule test
```

## Future: Graph Ontology Integration (v2)

When Ruby stack is ready, v2 will integrate:

- **FalkorDB**: Graph database for structural relationships
- **pgvector**: Semantic embeddings for similarity search
- **ruby_llm**: Local LLM via Ramalama
- **MCP**: Model Context Protocol for tool exposure

This enables:
- Semantic search for "roles related to nginx hardening"
- Graph traversal for "all variables consumed by this task"
- AI-powered refactoring suggestions
- Autonomous dependency resolution
