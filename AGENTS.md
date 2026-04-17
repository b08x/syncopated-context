## Universal Rules

### Path Resolution
**USE `Path(__file__)` for directory-agnostic script paths**
- Define `SCRIPT_DIR = Path(__file__).parent.resolve()` at module level.
- Construct all resource paths relative to `SCRIPT_DIR` (e.g., `SCRIPT_DIR / "config" / "settings.json"`).
- For subprocess calls, use absolute paths: `subprocess.run([str(SCRIPT_DIR / "helper.py")])`.
- **TEST** by running the script from `/tmp` or another arbitrary directory.

**DO NOT use hardcoded relative paths** in:
- File operations (`open()`, `Path("data/...")`)
- Subprocess calls (`subprocess.run(["python", "scripts/..."])`)
- Import statements (use package-relative imports instead)

**WHEN resolving paths in other languages**, use equivalents:
- Bash: `DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"`
- Node.js: `const __dirname = path.dirname(fileURLToPath(import.meta.url))`
- Ruby: `File.expand_path("..", __FILE__)`

---

### Date/Time Handling
**USE inclusive date ranges for "last N days"**
- `"last N days"` = today + N previous days (total N+1 days).
- Example: `"last 2 days"` → `[today, yesterday, day-before]` (3 days).

**WHEN working with timestamps across languages**:
1. Check the unit (seconds vs milliseconds) via sample queries.
2. For SQLite → JavaScript: multiply by 1000 if stored as seconds.
3. Use `datetime.fromtimestamp(ts)` (Python) or `new Date(ts * 1000)` (JS) as appropriate.

---

### CLI Tool Integration
**ALWAYS verify CLI syntax with `--help` before implementation**
- Test simple commands manually before scripting.
- **DO NOT assume** common flag patterns (e.g., `--format json` may not exist).

**WHEN spawning long-running CLI servers** (e.g., `ck --serve`):
- Set `cwd` explicitly in the process config (not via command-line args).
- Use separate processes for distinct working directories.
- Example (Ruby/Open3):
  ```ruby
  Open3.popen3("ck --serve", chdir: "/target/path") { |i, o, e, t| ... }
  ```

**WHEN using stdin-based tools** (e.g., `gum filter`, `fzf`):
- Pipe output (`fd ... | tool`) instead of using `-exec`/`-X`.
- Reserve `-exec` for tools that accept file arguments (e.g., `chmod`, `rm`).

---

### Data Serialization
**FOR dataclass JSON serialization**:
1. Import `asdict` from `dataclasses`.
2. Convert nested objects recursively:
   ```python
   data = asdict(obj)
   if "timestamp" in data:
       data["timestamp"] = data["timestamp"].isoformat()
   ```
3. Serialize with `json.dumps(data)`.

**WHEN handling special fields** (datetime, UUID, etc.):
- Pre-process the dictionary before serialization.
- Use custom encoders (e.g., `json.dumps(data, default=str)`) as a last resort.

---

### Process Management
**ALWAYS clean up MCP/stdio clients**
- Wrap usage in `ensure` blocks:
  ```ruby
  clients = indexes.map { |name| IndexManager.client_for(name) }
  begin
    # Query logic
  ensure
    clients.each(&:stop) # Prevent orphaned processes
  end
  ```
- For CLI tools, trap signals (e.g., `Signal.trap("INT") { cleanup }`).

---

### Bash Scripting
**USE `${array[@]+"${array[@]}"}` for empty arrays with `set -u`**
- Safer than disabling `set -u` or using `"${array[@]-}"`.
- Applies to both `${array[@]}` and `${array[*]}`.

**WHEN passing regex patterns to `awk` via `-v`**:
- Escape backslashes in the shell:
  ```bash
  awk -v pattern="${regex//\\/\\\\}" '...'
  ```
- Example: `\d` → `\\d` in the variable.

**FOR `fd` commands**:
- Always provide a pattern (even `.`) before directory args:
  ```bash
  fd . "${dir}"  # Correct
  fd "${dir}"    # Incorrect (treats dir as pattern)
  ```
- Use pipes (`|`) for stdin tools, `-exec` for file-arg tools.

**WHEN replacing `awk` field selection with `choose`**:
- Subtract 1 from field indices (0-based vs 1-based):
  ```bash
  awk '{print $3}'  →  choose 2
  ```

---

### Debugging
**WHEN paths fail in scripts**:
1. Print the resolved path: `print(f"Looking for config at: {CONFIG_PATH.absolute()}")`.
2. Test from a different directory: `cd /tmp && python script.py`.
3. Verify file existence: `assert CONFIG_PATH.exists()`.

**WHEN timestamps seem incorrect**:
1. Query a sample: `SELECT timestamp FROM table LIMIT 1`.
2. Compare against known events (e.g., current time).
3. Check for unit mismatches (seconds vs milliseconds).

---

## Project Context

This is a **multi-plugin marketplace repository** (`syncopated-context`) distributing:
- **rubysmithing** — Ruby development suite with 13+ SFL-persona agents
- **bashsmithing** — Bash development with shellcheck, BATS, TUI scaffolding
- **recall** — Multi-platform AI session analysis

Primary context: See `CLAUDE.md` for full repo structure and commands.

---

## Project-Specific Rules

### [Gemini CLI]
**USE updated session paths for v1.2+**
1. Read `~/.gemini/projects.json` to map project names → hashes.
2. Scan `~/.gemini/tmp/<hash>/chats/` for session JSON files.
3. Fall back to `~/.gemini/antigravity/conversations/` for pre-v1.2.

**WHEN exporting sessions**:
- List sessions first: `claude-sessions list`.
- Export by path: `claude-sessions export /path/to/session.jsonl` (not by ID).
- For bulk export: `claude-sessions export --all` or `--today`.

---

### [Hermes]
**FOR SQLite timestamps**:
- Timestamps are **seconds** (not milliseconds) since epoch.
- Use `datetime.fromtimestamp(ts)` (Python) or `new Date(ts * 1000)` (JS).

**WHEN exporting sessions**:
- **DO NOT use `--format` or `--days` flags** (not supported).
- Default output is JSONL; no format specification needed.

---

### [ruby_llm-mcp]
**FOR 0.8.0 stdio transport**:
- **WORKAROUND `cwd` dropping**: Wrap commands in:
  ```ruby
  "sh -c 'cd PATH && exec COMMAND'"
  ```
- **OR monkey-patch** the gem to pass `cwd` to `Open3.popen3`.

---

### [yadm]
**USE expanded paths for file operations**
- Replace `~` with `$HOME` or absolute paths.
- Validate paths with `list_directory` before writes.

---

### [Context7]
**FOR `resolve-library-id` tool calls**:
- Explicitly include `libraryName: <path>` in the parameters.
- **DO NOT rely on positional argument order**.

---

### [ck_agent]
**FOR `ck --serve` integration**:
- Set `cwd` in the MCP config (not via command-line args):
  ```json
  {
    "mcpServers": {
      "ck": {
        "command": "ck",
        "args": ["--serve"],
        "cwd": "/target/path"
      }
    }
  }
  ```
- Spawn separate processes for distinct folders.

---

### [RubyLLM]
**FOR streaming responses**:
- Access text fragments via `chunk.content`.
- **DO NOT use** `chunk.inspect` in production code.

---

### Development Commands

**Ruby development** (rubysmithing plugin):
```bash
cd plugins/rubysmithing && bundle install
bundle exec rubocop              # Lint
bundle exec rubocop -a           # Autocorrect
bundle exec rspec                # Tests
bundle exec rspec spec/path/to/file_spec.rb  # Single test
```

**Bash development** (bashsmithing plugin):
```bash
shellcheck scripts/**/*.sh       # Lint
bats test/**/*.bats            # Run BATS tests
```

**Core workflow commands**:
```bash
/implement     # Implementation planning
/refactor     # Code refactoring
/containerize  # Docker workflows
/recall        # Multi-platform session analysis
```

---

### Skill Invocation Rule

**The skill name defines the WORKFLOW, not the artifact.**
- `/github-issues` → use issue tracking workflow (don't create implementation code)
- `/refactor` → refactor existing code (don't create new files)

---

### Codemap and Context7

**Use Codemap CLI for Codebase Navigation**:
```bash
codemap .                    # Project tree
codemap --diff               # What changed vs main branch
codemap --deps .             # Dependency flow
```

**Use Context7 MCP for Loading Documentation**:
- `/crewaiinc/crewai` - Main CrewAI docs
- `/beaconbay/ck` - ck (seek): semantic code search
- `/neolabhq/context-engineering-kit` - Context engineering techniques

---

### /graphify

Use `/graphify` skill to convert any input (code, docs, papers, images) → knowledge graph → clustered communities → HTML + JSON + audit report