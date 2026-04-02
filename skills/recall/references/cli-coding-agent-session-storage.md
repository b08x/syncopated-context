# DeepWiki Q&A with Code Context for Repository: b08x/code-insights
## Q1
elaborate on discovering, identifying, and parsing conversation data for each of the session providers; the intent to reuse the patterns in a python script that also analyses session data
be sure to include specifics on gemini-cli and hermes-agent sessions
### Answer
# Session Provider Architecture for Conversation Data

The Code Insights system uses a provider pattern to discover and parse conversation data from various AI tools. Each provider implements the `SessionProvider` interface, normalizing different data formats into a common `ParsedSession` structure code-insights:86-94 .

## Provider Interface Pattern

All session providers follow this contract:

```typescript
interface SessionProvider {
  getProviderName(): string;                                    // e.g. 'claude-code', 'cursor'
  discover(options?: { projectFilter?: string }): Promise<string[]>;  // Find session files
  parse(filePath: string): Promise<ParsedSession | null>;       // Parse into common format
}
``` code-insights:86-94 

Providers are registered in a central registry code-insights:1-60 .

## Discovery Patterns

### Gemini CLI Provider
Discovers JSON session files in `~/.gemini/tmp/<project_hash>/chats/`:

1. Scans the tmp directory for project folders (hashed or named)
2. Loads project mappings from `projects.json` if available
3. Filters by project name if specified
4. Returns paths to `.json` files in `chats/` subdirectories code-insights:18-67 

### Hermes Agent Provider
Discovers sessions from SQLite database at `~/.hermes/state.db`:

1. Opens the database in read-only mode
2. Queries the `sessions` table for session IDs and titles
3. Filters by title if project filter specified
4. Returns virtual paths in format `<db_path>#<session_id>` code-insights:17-47 

## Parsing Patterns

### Gemini CLI Parsing
Parses JSON session files with this structure:

```json
{
  "sessionId": "uuid",
  "startTime": "timestamp",
  "lastUpdated": "timestamp", 
  "messages": [
    {
      "id": "msg-id",
      "type": "user|gemini|info",
      "content": "string or array",
      "timestamp": "timestamp",
      "toolCalls": [...],
      "tokens": {...}
    }
  ]
}
```

The provider:
- Extracts content from string or array formats
- Parses tool calls and results
- Calculates usage metrics from token data
- Resolves project info from `.project_root` file code-insights:69-149 

### Hermes Agent Parsing
Parses from SQLite with `sessions` and `messages` tables:

1. Queries session metadata from `sessions` table
2. Fetches ordered messages from `messages` table
3. Handles tool results by attaching to previous assistant messages
4. Parses JSON tool calls from string column
5. Builds usage from session-level token counts code-insights:49-171 

## Normalization to Common Schema

Both providers normalize to `ParsedSession` with:
- Standardized message types (`user`, `assistant`, `system`)
- Unified tool call/result structure
- Common usage metrics (tokens, cost)
- Consistent timestamp handling
- Project metadata extraction code-insights:59-83 

## Reusable Patterns for Python

To implement similar providers in Python:

1. **Interface Definition**: Create an abstract base class with `discover()` and `parse()` methods
2. **Discovery Strategy**: 
   - File system scanning for JSON/JSONL formats
   - Database queries for SQLite sources
   - Virtual path handling for database-based sessions
3. **Parsing Pipeline**:
   - Raw data validation
   - Message type normalization
   - Tool call/result extraction
   - Usage metric calculation
   - Project metadata resolution
4. **Error Handling**: Graceful fallbacks for malformed data
5. **Configuration**: Platform-specific path resolution

The key insight is separating discovery (finding data sources) from parsing (normalizing data), allowing each provider to handle its unique format while producing a consistent output structure.

## Notes

- The provider registry pattern allows easy addition of new sources code-insights:42-58 
- Virtual paths (`db#id`) enable database-based sessions to work with file-based APIs
- All providers handle platform-specific paths through utility functions code-insights:89-106 
- Test files show expected data structures and edge cases code-insights:57-163 code-insights:63-131 

Wiki pages you might want to explore:
- [Overview (b08x/code-insights)](/wiki/b08x/code-insights#1)
- [Glossary (b08x/code-insights)](/wiki/b08x/code-insights#8)
### Citations
**File:** cli/src/providers/registry.ts (L1-60)
```typescript
import type { SessionProvider } from './types.js';
import { ClaudeCodeProvider } from './claude-code.js';
import { CursorProvider } from './cursor.js';
import { CodexProvider } from './codex.js';
import { CopilotCliProvider } from './copilot-cli.js';
import { CopilotProvider } from './copilot.js';
import { GeminiCliProvider } from './gemini-cli.js';
import { HermesAgentProvider } from './hermes-agent.js';
import { OpenCodeProvider } from './opencode.js';
import { CrushProvider } from './crush.js';

const providers = new Map<string, SessionProvider>();

// Register built-in providers
const claudeCode = new ClaudeCodeProvider();
providers.set(claudeCode.getProviderName(), claudeCode);

const cursor = new CursorProvider();
providers.set(cursor.getProviderName(), cursor);

const codex = new CodexProvider();
providers.set(codex.getProviderName(), codex);

const copilotCli = new CopilotCliProvider();
providers.set(copilotCli.getProviderName(), copilotCli);

const copilot = new CopilotProvider();
providers.set(copilot.getProviderName(), copilot);

const geminiCli = new GeminiCliProvider();
providers.set(geminiCli.getProviderName(), geminiCli);

const hermesAgent = new HermesAgentProvider();
providers.set(hermesAgent.getProviderName(), hermesAgent);

const opencode = new OpenCodeProvider();
providers.set(opencode.getProviderName(), opencode);

const crush = new CrushProvider();
providers.set(crush.getProviderName(), crush);

/**
 * Get a provider by name
 */
export function getProvider(name: string): SessionProvider {
  const provider = providers.get(name);
  if (!provider) {
    throw new Error(`Unknown provider: ${name}`);
  }
  return provider;
}

/**
 * Get all registered providers
 */
export function getAllProviders(): SessionProvider[] {
  return [...providers.values()];
}


```
**File:** cli/src/providers/gemini-cli.ts (L18-67)
```typescript
  async discover(options?: { projectFilter?: string }): Promise<string[]> {
    const tmpDir = getGeminiTmpDir();
    const projectsFile = path.join(getGeminiHomeDir(), 'projects.json');

    if (!fs.existsSync(tmpDir)) {
      return [];
    }

    const sessionFiles: string[] = [];
    const projectMappings: Record<string, string> = {};

    // 1. Load project mappings from projects.json if available
    if (fs.existsSync(projectsFile)) {
      try {
        const content = fs.readFileSync(projectsFile, 'utf-8');
        const data = JSON.parse(content);
        if (data.projects) {
          Object.assign(projectMappings, data.projects);
        }
      } catch (err) {
        console.warn(`[gemini-cli] Failed to read projects.json: ${err}`);
      }
    }

    // 2. Scan tmp directory for project folders (hash or name)
    const entries = fs.readdirSync(tmpDir);
    for (const entry of entries) {
      const projectDir = path.join(tmpDir, entry);
      if (!fs.statSync(projectDir).isDirectory()) continue;

      // Check if it's a project we care about if filter is provided
      if (options?.projectFilter && !entry.toLowerCase().includes(options.projectFilter.toLowerCase())) {
        // We might still care if the real project name (from mapping) matches
        const realName = projectMappings[entry] || entry;
        if (!realName.toLowerCase().includes(options.projectFilter.toLowerCase())) {
          continue;
        }
      }

      const chatsDir = path.join(projectDir, 'chats');
      if (fs.existsSync(chatsDir) && fs.statSync(chatsDir).isDirectory()) {
        const files = fs.readdirSync(chatsDir).filter(f => f.endsWith('.json'));
        for (const file of files) {
          sessionFiles.push(path.join(chatsDir, file));
        }
      }
    }

    return sessionFiles;
  }
```
**File:** cli/src/providers/gemini-cli.ts (L69-149)
```typescript
  async parse(filePath: string): Promise<ParsedSession | null> {
    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const data = JSON.parse(content);

      if (!data.sessionId || !Array.isArray(data.messages)) {
        return null;
      }

      // Resolve project info
      const projectDir = path.dirname(path.dirname(filePath));
      const projectId = path.basename(projectDir);
      let projectPath = '';
      let projectName = projectId;

      const projectRootFile = path.join(projectDir, '.project_root');
      if (fs.existsSync(projectRootFile)) {
        projectPath = fs.readFileSync(projectRootFile, 'utf-8').trim();
        projectName = path.basename(projectPath);
      }

      const messages: ParsedMessage[] = [];
      let userMessageCount = 0;
      let assistantMessageCount = 0;
      let toolCallCount = 0;

      for (const msg of data.messages) {
        if (msg.type === 'info') continue; // Skip info messages

        const parsedMsg: ParsedMessage = {
          id: msg.id || crypto.randomUUID(),
          sessionId: data.sessionId,
          type: msg.type === 'gemini' ? 'assistant' : (msg.type === 'user' ? 'user' : 'system'),
          content: this.extractContent(msg),
          thinking: this.extractThinking(msg),
          toolCalls: this.extractToolCalls(msg),
          toolResults: this.extractToolResults(msg),
          usage: this.extractUsage(msg),
          timestamp: new Date(msg.timestamp),
          parentId: null, // Gemini CLI format doesn't seem to have explicit parents in the JSON
        };

        if (parsedMsg.type === 'user') userMessageCount++;
        if (parsedMsg.type === 'assistant') assistantMessageCount++;
        toolCallCount += parsedMsg.toolCalls.length;

        messages.push(parsedMsg);
      }

      if (messages.length === 0) return null;

      const sessionUsage = this.calculateSessionUsage(messages);

      return {
        id: data.sessionId,
        projectPath,
        projectName,
        summary: null,
        generatedTitle: null,
        titleSource: null,
        sessionCharacter: null,
        startedAt: new Date(data.startTime || messages[0].timestamp),
        endedAt: new Date(data.lastUpdated || messages[messages.length - 1].timestamp),
        messageCount: messages.length,
        userMessageCount,
        assistantMessageCount,
        toolCallCount,
        compactCount: 0,
        autoCompactCount: 0,
        slashCommands: [],
        gitBranch: null,
        claudeVersion: null,
        sourceTool: 'gemini-cli',
        usage: sessionUsage,
        messages,
      };
    } catch (err) {
      console.error(`[gemini-cli] Failed to parse ${filePath}: ${err}`);
      return null;
    }
  }
```
**File:** cli/src/providers/hermes-agent.ts (L17-47)
```typescript
  async discover(options?: { projectFilter?: string }): Promise<string[]> {
    const homeDir = getHermesHomeDir();
    const dbPath = path.join(homeDir, 'state.db');

    if (!fs.existsSync(dbPath)) {
      return [];
    }

    let db: InstanceType<typeof Database> | null = null;
    try {
      db = new Database(dbPath, { readonly: true, fileMustExist: true });
      
      const sessions = db.prepare('SELECT id, title FROM sessions').all() as { id: string, title: string | null }[];
      
      const virtualPaths: string[] = [];
      for (const session of sessions) {
        // Apply project filter if specified (check title)
        if (options?.projectFilter && session.title && !session.title.toLowerCase().includes(options.projectFilter.toLowerCase())) {
          continue;
        }
        virtualPaths.push(`${dbPath}#${session.id}`);
      }
      
      return virtualPaths;
    } catch (err) {
      console.error(`[hermes-agent] Failed to discover sessions: ${err}`);
      return [];
    } finally {
      db?.close();
    }
  }
```
**File:** cli/src/providers/hermes-agent.ts (L49-171)
```typescript
  async parse(virtualPath: string): Promise<ParsedSession | null> {
    const hashIndex = virtualPath.lastIndexOf('#');
    if (hashIndex === -1) return null;

    const dbPath = virtualPath.slice(0, hashIndex);
    const sessionId = virtualPath.slice(hashIndex + 1);

    let db: InstanceType<typeof Database> | null = null;
    try {
      db = new Database(dbPath, { readonly: true, fileMustExist: true });

      const sessionRow = db.prepare('SELECT * FROM sessions WHERE id = ?').get(sessionId) as any;
      if (!sessionRow) return null;

      const messageRows = db.prepare('SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC').all(sessionId) as any[];

      const messages: ParsedMessage[] = [];
      let userMessageCount = 0;
      let assistantMessageCount = 0;
      let toolCallCount = 0;

      for (const row of messageRows) {
        if (row.role === 'tool') {
          // Attach to the last assistant message as a tool result
          const lastAssistant = messages.reverse().find(m => m.type === 'assistant');
          messages.reverse(); // back to original order

          if (lastAssistant) {
            lastAssistant.toolResults.push({
              toolUseId: row.tool_call_id || `tool-${row.id}`,
              output: row.content || '',
            });
            continue;
          }
        }

        const type = row.role === 'assistant' ? 'assistant' : (row.role === 'user' ? 'user' : 'system');
        const toolCalls: ToolCall[] = [];
        if (row.tool_calls) {
          try {
            const parsedCalls = JSON.parse(row.tool_calls);
            if (Array.isArray(parsedCalls)) {
              for (const tc of parsedCalls) {
                toolCalls.push({
                  id: tc.id,
                  name: tc.name || tc.function?.name || 'unknown',
                  input: tc.args || tc.function?.arguments || {},
                });
              }
            }
          } catch {
            // Ignore parse errors
          }
        }

        const parsedMsg: ParsedMessage = {
          id: `hermes-${row.id}`,
          sessionId: `hermes-agent:${sessionId}`,
          type,
          content: row.content || '',
          thinking: row.reasoning || null,
          toolCalls,
          toolResults: [],
          usage: row.token_count ? {
            inputTokens: 0, // Hermes doesn't seem to store per-message input tokens in the messages table
            outputTokens: row.token_count,
            cacheCreationTokens: 0,
            cacheReadTokens: 0,
            model: sessionRow.model || 'unknown',
            estimatedCostUsd: 0, // Will be calculated at session level
          } : null,
          timestamp: new Date(row.timestamp * 1000),
          parentId: null,
        };

        if (parsedMsg.type === 'user') userMessageCount++;
        if (parsedMsg.type === 'assistant') assistantMessageCount++;
        toolCallCount += toolCalls.length;

        messages.push(parsedMsg);
      }

      const sessionUsage: SessionUsage = {
        totalInputTokens: sessionRow.input_tokens || 0,
        totalOutputTokens: sessionRow.output_tokens || 0,
        cacheCreationTokens: sessionRow.cache_write_tokens || 0,
        cacheReadTokens: sessionRow.cache_read_tokens || 0,
        estimatedCostUsd: sessionRow.actual_cost_usd || sessionRow.estimated_cost_usd || 0,
        modelsUsed: sessionRow.model ? [sessionRow.model] : [],
        primaryModel: sessionRow.model || 'unknown',
        usageSource: 'session',
      };

      return {
        id: `hermes-agent:${sessionId}`,
        projectPath: '', // Hermes Agent sessions are global or project-unaware in the DB
        projectName: sessionRow.title || 'hermes-agent-session',
        summary: null,
        generatedTitle: sessionRow.title || null,
        titleSource: sessionRow.title ? 'insight' : null,
        sessionCharacter: null,
        startedAt: new Date(sessionRow.started_at * 1000),
        endedAt: sessionRow.ended_at ? new Date(sessionRow.ended_at * 1000) : new Date(sessionRow.started_at * 1000),
        messageCount: messages.length,
        userMessageCount,
        assistantMessageCount,
        toolCallCount,
        compactCount: 0,
        autoCompactCount: 0,
        slashCommands: [],
        gitBranch: null,
        claudeVersion: null,
        sourceTool: 'hermes-agent',
        usage: sessionUsage,
        messages,
      };
    } catch (err) {
      console.error(`[hermes-agent] Failed to parse session ${sessionId}: ${err}`);
      return null;
    } finally {
      db?.close();
    }
  }
```
**File:** cli/src/utils/config.ts (L89-106)
```typescript
/**
 * Get Gemini CLI home directory
 */
export function getGeminiHomeDir(): string {
  return path.join(os.homedir(), '.gemini');
}

/**
 * Get Gemini CLI temporary directory (where sessions are stored)
 */
export function getGeminiTmpDir(): string {
  return path.join(getGeminiHomeDir(), 'tmp');
}

/**
 * Get Hermes Agent home directory
 */
export function getHermesHomeDir(): string {
```
**File:** cli/src/providers/__tests__/gemini-cli.test.ts (L57-163)
```typescript
describe('GeminiCliProvider', () => {
  let tempHomeDir: string;
  let tempTmpDir: string;
  const provider = new GeminiCliProvider();

  beforeEach(() => {
    tempHomeDir = fs.mkdtempSync(path.join(os.tmpdir(), 'gemini-home-'));
    tempTmpDir = path.join(tempHomeDir, 'tmp');
    fs.mkdirSync(tempTmpDir);

    vi.mocked(getGeminiHomeDir).mockReturnValue(tempHomeDir);
    vi.mocked(getGeminiTmpDir).mockReturnValue(tempTmpDir);
  });

  afterEach(() => {
    fs.rmSync(tempHomeDir, { recursive: true, force: true });
  });

  it('returns "gemini-cli" as provider name', () => {
    expect(provider.getProviderName()).toBe('gemini-cli');
  });

  describe('discover', () => {
    it('discovers session files in hashed directories', async () => {
      const projectHash = '566bb2a8ae4604bf4ed6f1606f2a1401987f961737a1e39455da5183d58aa75b';
      const projectDir = path.join(tempTmpDir, projectHash);
      const chatsDir = path.join(projectDir, 'chats');
      fs.mkdirSync(chatsDir, { recursive: true });
      
      const sessionFile = path.join(chatsDir, 'session-1.json');
      fs.writeFileSync(sessionFile, JSON.stringify(VALID_GEMINI_SESSION));

      const discovered = await provider.discover();
      expect(discovered).toContain(sessionFile);
    });

    it('discovers session files in named directories', async () => {
      const projectName = 'my-cool-project';
      const projectDir = path.join(tempTmpDir, projectName);
      const chatsDir = path.join(projectDir, 'chats');
      fs.mkdirSync(chatsDir, { recursive: true });
      
      const sessionFile = path.join(chatsDir, 'session-1.json');
      fs.writeFileSync(sessionFile, JSON.stringify(VALID_GEMINI_SESSION));

      const discovered = await provider.discover();
      expect(discovered).toContain(sessionFile);
    });

    it('filters discovered files by project name', async () => {
      const project1Dir = path.join(tempTmpDir, 'project-alpha', 'chats');
      const project2Dir = path.join(tempTmpDir, 'project-beta', 'chats');
      fs.mkdirSync(project1Dir, { recursive: true });
      fs.mkdirSync(project2Dir, { recursive: true });
      
      const file1 = path.join(project1Dir, 'session.json');
      const file2 = path.join(project2Dir, 'session.json');
      fs.writeFileSync(file1, JSON.stringify(VALID_GEMINI_SESSION));
      fs.writeFileSync(file2, JSON.stringify(VALID_GEMINI_SESSION));

      const discovered = await provider.discover({ projectFilter: 'alpha' });
      expect(discovered).toContain(file1);
      expect(discovered).not.toContain(file2);
    });
  });

  describe('parse', () => {
    it('parses a valid Gemini session file', async () => {
      const projectDir = path.join(tempTmpDir, 'test-project');
      const chatsDir = path.join(projectDir, 'chats');
      fs.mkdirSync(chatsDir, { recursive: true });
      
      // Create .project_root
      const projectRoot = '/Users/test/projects/my-project';
      fs.writeFileSync(path.join(projectDir, '.project_root'), projectRoot);

      const filePath = path.join(chatsDir, 'session.json');
      fs.writeFileSync(filePath, JSON.stringify(VALID_GEMINI_SESSION));

      const session = await provider.parse(filePath);

      expect(session).not.toBeNull();
      expect(session!.id).toBe(VALID_GEMINI_SESSION.sessionId);
      expect(session!.projectPath).toBe(projectRoot);
      expect(session!.projectName).toBe('my-project');
      expect(session!.sourceTool).toBe('gemini-cli');
      expect(session!.messageCount).toBe(2);
      expect(session!.userMessageCount).toBe(1);
      expect(session!.assistantMessageCount).toBe(1);
      
      const assistantMsg = session!.messages.find(m => m.type === 'assistant');
      expect(assistantMsg!.content).toBe(VALID_GEMINI_SESSION.messages[1].content);
      expect(assistantMsg!.thinking).toContain('Greeting');
      expect(assistantMsg!.usage).not.toBeNull();
      expect(assistantMsg!.usage!.inputTokens).toBe(100);
      expect(assistantMsg!.usage!.outputTokens).toBe(50);
    });

    it('returns null for invalid session files', async () => {
      const filePath = path.join(tempTmpDir, 'invalid.json');
      fs.writeFileSync(filePath, JSON.stringify({ foo: 'bar' }));

      const session = await provider.parse(filePath);
      expect(session).toBeNull();
    });
  });
});
```
**File:** cli/src/providers/__tests__/hermes-agent.test.ts (L63-131)
```typescript
describe('HermesAgentProvider', () => {
  let tempHomeDir: string;
  let dbPath: string;
  const provider = new HermesAgentProvider();

  beforeEach(() => {
    tempHomeDir = fs.mkdtempSync(path.join(os.tmpdir(), 'hermes-home-'));
    dbPath = path.join(tempHomeDir, 'state.db');
    fs.writeFileSync(dbPath, ''); // Create dummy file

    vi.mocked(getHermesHomeDir).mockReturnValue(tempHomeDir);
  });

  afterEach(() => {
    fs.rmSync(tempHomeDir, { recursive: true, force: true });
  });

  it('returns "hermes-agent" as provider name', () => {
    expect(provider.getProviderName()).toBe('hermes-agent');
  });

  describe('discover', () => {
    it('discovers session virtual paths from the database', async () => {
      const discovered = await provider.discover();
      expect(discovered).toContain(`${dbPath}#session-1`);
    });

    it('filters sessions by title', async () => {
      const discovered = await provider.discover({ projectFilter: 'Test' });
      expect(discovered).toContain(`${dbPath}#session-1`);

      const filtered = await provider.discover({ projectFilter: 'None' });
      expect(filtered).not.toContain(`${dbPath}#session-1`);
    });
  });

  describe('parse', () => {
    it('parses a valid Hermes Agent session from the database', async () => {
      const virtualPath = `${dbPath}#session-1`;
      const session = await provider.parse(virtualPath);

      expect(session).not.toBeNull();
      expect(session!.id).toBe('hermes-agent:session-1');
      expect(session!.projectName).toBe('Test Session');
      expect(session!.sourceTool).toBe('hermes-agent');
      expect(session!.messageCount).toBe(3); // user, assistant (with tool result), assistant
      expect(session!.userMessageCount).toBe(1);
      expect(session!.assistantMessageCount).toBe(2);
      expect(session!.toolCallCount).toBe(1);
      
      const firstAssistant = session!.messages[1];
      expect(firstAssistant.type).toBe('assistant');
      expect(firstAssistant.toolCalls).toHaveLength(1);
      expect(firstAssistant.toolResults).toHaveLength(1);
      expect(firstAssistant.toolResults[0].output).toBe('{"result": "found nothing"}');

      expect(session!.usage).not.toBeUndefined();
      expect(session!.usage!.totalInputTokens).toBe(100);
      expect(session!.usage!.totalOutputTokens).toBe(50);
      expect(session!.usage!.estimatedCostUsd).toBe(0.01);
    });

    it('returns null for non-existent session', async () => {
      const virtualPath = `${dbPath}#non-existent`;
      const session = await provider.parse(virtualPath);
      expect(session).toBeNull();
    });
  });
});
```
