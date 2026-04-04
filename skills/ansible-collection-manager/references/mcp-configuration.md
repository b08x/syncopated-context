# MCP Server Configuration Examples

This directory contains configuration examples for exposing the Ansible Collection Manager tools via MCP to various GenAI CLI applications.

## Server Architecture

The MCP server (`scripts/mcp_server.py`) exposes 5 tools:

1. **ansible_analyze_collection** - Collection structure and complexity analysis
2. **ansible_detect_antipatterns** - Security vulnerabilities and code smell detection
3. **ansible_consolidate_packages** - Package duplication analysis and consolidation planning
4. **ansible_analyze_variables** - Variable precedence tracing and shadowing detection
5. **ansible_map_dependencies** - Role dependency mapping and graph generation

## Configuration by CLI Tool

### Claude Code

**Location:** `~/.config/claude-code/mcp_servers.json`

```json
{
  "mcpServers": {
    "ansible-collection-manager": {
      "command": "python3",
      "args": [
        "/path/to/ansible-collection-manager/scripts/mcp_server.py"
      ],
      "transport": "stdio"
    }
  }
}
```

### Gemini CLI

**Location:** `~/.config/gemini-cli/mcp_servers.json`

```json
{
  "servers": {
    "ansible-collection-manager": {
      "command": "python3",
      "args": [
        "/path/to/ansible-collection-manager/scripts/mcp_server.py"
      ],
      "protocol": "stdio"
    }
  }
}
```

### Antigravity

**Location:** `~/.antigravity/mcp_config.json`

```json
{
  "mcp_servers": {
    "ansible-collection-manager": {
      "command": "python3",
      "args": [
        "/path/to/ansible-collection-manager/scripts/mcp_server.py"
      ],
      "transport": "stdio"
    }
  }
}
```

### OpenCode with oh-my-opencode

**Location:** `~/.config/opencode/mcp_servers.json`

```json
{
  "servers": [
    {
      "name": "ansible-collection-manager",
      "command": "python3",
      "args": [
        "/path/to/ansible-collection-manager/scripts/mcp_server.py"
      ],
      "transport": "stdio"
    }
  ]
}
```

## Testing the MCP Server

### Manual Test (JSON-RPC over stdio)

```bash
# Start the server
python3 scripts/mcp_server.py

# Send a tools/list request
{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}

# Send a tools/call request
{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "ansible_analyze_collection", "arguments": {"collection_path": "/path/to/collection"}}}
```

### Test with MCP Inspector (if available)

```bash
# Install MCP inspector
npm install -g @modelcontextprotocol/inspector

# Test the server
mcp-inspector python3 scripts/mcp_server.py
```

## Tool Usage Examples

Once configured, the CLI tools can invoke these tools:

### Example 1: Collection Analysis

**User prompt:**
```
"Analyze the structure of my Ansible collection at ~/ansible-rhel-workstation-builder"
```

**MCP tool call:**
```json
{
  "name": "ansible_analyze_collection",
  "arguments": {
    "collection_path": "~/ansible-rhel-workstation-builder",
    "format": "text"
  }
}
```

### Example 2: Security Audit

**User prompt:**
```
"Find critical security issues in my collection"
```

**MCP tool call:**
```json
{
  "name": "ansible_detect_antipatterns",
  "arguments": {
    "collection_path": "~/ansible-rhel-workstation-builder",
    "severity": "CRITICAL",
    "format": "text"
  }
}
```

### Example 3: Package Consolidation

**User prompt:**
```
"Help me consolidate packages - create a consolidation plan"
```

**MCP tool call:**
```json
{
  "name": "ansible_consolidate_packages",
  "arguments": {
    "collection_path": "~/ansible-rhel-workstation-builder",
    "include_plan": true,
    "format": "text"
  }
}
```

### Example 4: Variable Analysis

**User prompt:**
```
"Trace the precedence for the db_password variable"
```

**MCP tool call:**
```json
{
  "name": "ansible_analyze_variables",
  "arguments": {
    "collection_path": "~/ansible-rhel-workstation-builder",
    "variable_name": "db_password",
    "format": "text"
  }
}
```

### Example 5: Dependency Mapping

**User prompt:**
```
"Show me role dependencies and generate a Mermaid graph"
```

**MCP tool call:**
```json
{
  "name": "ansible_map_dependencies",
  "arguments": {
    "collection_path": "~/ansible-rhel-workstation-builder",
    "format": "mermaid"
  }
}
```

## Troubleshooting

### Server doesn't start

**Check Python version:**
```bash
python3 --version  # Should be 3.9+
```

**Check PyYAML:**
```bash
pip3 show pyyaml
```

**Check script permissions:**
```bash
chmod +x scripts/mcp_server.py
```

### Tools not showing in CLI

**Verify configuration path:**
- Each CLI tool looks in different locations
- Use absolute paths for `command` and script args

**Test server manually:**
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python3 scripts/mcp_server.py
```

### Tool execution fails

**Check collection path:**
- Must be absolute path or expandable (~)
- Collection root must contain roles/ or playbooks/

**Check timeouts:**
- Large collections may take >30s to analyze
- Server has 5-minute timeout per tool

**Check logs:**
- Most CLI tools have verbose modes
- Look for MCP protocol errors

## Environment Variables

Optional environment variables for debugging:

```bash
# Enable debug logging
export MCP_DEBUG=1

# Set custom timeout (seconds)
export MCP_TIMEOUT=600

# Use custom scripts directory
export ANSIBLE_TOOLS_DIR=/path/to/scripts
```

## Security Considerations

The MCP server:
- **Read-only:** All analysis scripts are non-destructive
- **No network:** Scripts only read local files
- **Sandboxed:** Runs with user permissions
- **Validated inputs:** Path traversal protection built-in

The server inherits the security context of the parent CLI application.

## Advanced Configuration

### Running as a Service

For persistent availability:

```bash
# systemd service example
[Unit]
Description=Ansible Collection Manager MCP Server
After=network.target

[Service]
Type=simple
User=your-user
ExecStart=/usr/bin/python3 /path/to/scripts/mcp_server.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Remote Access (via SSE)

For web-based or remote clients:

```python
# Wrap stdio server with HTTP/SSE transport
# See MCP specification for SSE transport details
```

### Custom Tool Configuration

To add new analysis tools:

1. Create Python script in `scripts/`
2. Add tool definition to `mcp_server.py:get_tool_definitions()`
3. Add tool-script mapping to `execute_tool()`
4. Update this documentation

## Integration with Future v2

When Ruby graph ontology stack is ready:

```json
{
  "mcpServers": {
    "ansible-collection-manager-v1": {
      "comment": "Static analysis tools",
      "command": "python3",
      "args": ["/path/to/v1/mcp_server.py"]
    },
    "ansible-graph-ontology-v2": {
      "comment": "Graph database queries",
      "command": "ruby",
      "args": ["/path/to/v2/ruby_llm-mcp", "falkordb-ansible"]
    }
  }
}
```

Both v1 and v2 servers can run simultaneously, giving CLI tools access to both static analysis and graph reasoning.
