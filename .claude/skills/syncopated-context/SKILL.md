```markdown
# syncopated-context Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill introduces the core development patterns, coding conventions, and workflow automation strategies used in the `syncopated-context` Ruby codebase. While the repository does not rely on a specific framework, it emphasizes modular design, clear file organization, and a set of well-defined, command-driven workflows for evolving plugins, agents, and data pipelines. This guide will help you contribute effectively by following established conventions and leveraging automation commands.

## Coding Conventions

### File Naming

- **Kebab-case** is used for all file names.
  - Example: `data-engineer.md`, `step-1-setup.md`

### Import and Export

- **Imports:** Use relative paths.
  - Example:
    ```ruby
    require_relative '../lib/my_module'
    ```
- **Exports:** Use named exports (Ruby modules/classes).
  - Example:
    ```ruby
    module MyModule
      def self.perform
        # ...
      end
    end
    ```

### Commit Messages

- **Conventional commit** style is enforced.
- Prefixes: `feat`, `refactor`, `chore`, `docs`, `fix`
- Example:
  ```
  feat: add schema extension workflow for data pipelines
  ```

## Workflows

### Add or Update Workflow Command

**Trigger:** When introducing a new automated workflow or skill-driven command to the plugin.  
**Command:** `/add-workflow-command`

1. **Create or update a command file** in `plugins/rubysmithing/commands/` (e.g., `flow.md`, `vibe.md`).
2. **Create a set of task step files** in `plugins/rubysmithing/tasks/<workflow>/` (e.g., `step-1-*.md`, `step-2-*.md`).
3. **Optionally update or create related agent or SKILL.md files** if the workflow is agent-driven.

**Example:**
```shell
/add-workflow-command
# Then create:
# plugins/rubysmithing/commands/audit.md
# plugins/rubysmithing/tasks/audit/step-1-init.md
# plugins/rubysmithing/tasks/audit/step-2-review.md
```

---

### Agent Rename and Migration

**Trigger:** When migrating agent naming conventions or refactoring agent roles.  
**Command:** `/rename-agent`

1. **Rename agent files** in `plugins/rubysmithing/agents/` from old to new names.
2. **Update all references** in `README.md`, `CLAUDE.md`, `SKILL.md`, and orchestrator/plan files.
3. **Remove or update migration reference tables** in `agents/README.md`.

**Example:**
```shell
/rename-agent
# Then update:
# plugins/rubysmithing/agents/old_name.md -> new_name.md
# All references in documentation and plans
```

---

### Sync READMEs and Changelog

**Trigger:** When updating documentation after adding features, workflows, or making major changes.  
**Command:** `/sync-readmes`

1. **Update `CHANGELOG.md`** with recent changes.
2. **Update `README.md` and `plugins/rubysmithing/README.md`** to reflect new workflows, skills, or architecture.
3. **Optionally update `CLAUDE.md` or other top-level docs**.

**Example:**
```shell
/sync-readmes
# Then edit:
# CHANGELOG.md
# README.md
# plugins/rubysmithing/README.md
```

---

### Schema or Data Pipeline Extension

**Trigger:** When adding a new data pipeline, search method, or extending the canonical schema.  
**Command:** `/extend-schema`

1. **Update agent or skill documentation** (e.g., `agentic-data-engineer.md`, `cognitive-architect.md`).
2. **Update or add references** (e.g., `gem-registry.md`).
3. **Update or add SKILL.md** for the relevant skill.
4. **Update or add task step files** in `tasks/schema/` and `tasks/vibe/step-4b-data-schema.md`.

**Example:**
```shell
/extend-schema
# Then update:
# plugins/rubysmithing/agents/agentic-data-engineer.md
# plugins/rubysmithing/skills/data-engineer/SKILL.md
# plugins/rubysmithing/tasks/schema/step-1-define.md
```

## Testing Patterns

- **Test files** follow the `*.test.*` pattern (e.g., `my_module.test.rb`).
- **Testing framework** is not specified; use idiomatic Ruby test patterns.
- Example test file:
  ```ruby
  # my_module.test.rb
  require_relative 'my_module'

  describe MyModule do
    it 'performs the expected action' do
      expect(MyModule.perform).to eq('expected result')
    end
  end
  ```

## Commands

| Command                | Purpose                                                         |
|------------------------|-----------------------------------------------------------------|
| /add-workflow-command  | Add or update a workflow command and its task chain             |
| /rename-agent          | Rename agents and update all references                         |
| /sync-readmes          | Synchronize README and CHANGELOG files with recent changes      |
| /extend-schema         | Extend or update the data schema and related documentation      |
```
