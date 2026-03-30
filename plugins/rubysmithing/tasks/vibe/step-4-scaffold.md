# Vibe — Step 4: Project Scaffold

You are the `platform-engineer` executing Step 4 of the `/rubysmithing:vibe` workflow.

## Your Input

Project Charter from Step 1 (name, archetype, complexity estimate).

## Your Task

Initialize the Ruby project using rubysmith or gemsmith based on the archetype.

## Instructions

1. Read `$CLAUDE_PLUGIN_ROOT/skills/scaffold/SKILL.md` for the complete scaffold workflow
2. Use the charter's `archetype` field to select the preset:
   - `tool` → rubysmith with CLI preset
   - `gem` → gemsmith
   - `app` → rubysmith with application preset
   - `service` → rubysmith with service preset
3. Use the charter's `Name` as the project name (snake_case)
4. Apply convention hardening after scaffold:
   - Add `.rubocop.yml` if not present
   - Add `frozen_string_literal: true` to generated files
   - Verify Zeitwerk loader is configured in the main entry point

## Output

Confirm:
- Project directory created at `./<name>`
- Entry point: `lib/<name>.rb` (or equivalent)
- Zeitwerk loader configured
- RuboCop or Standard configured
- Ready for first backlog task implementation
