#!/usr/bin/env python3
"""
Ansible Collection Manager MCP Server
Exposes collection analysis tools via Model Context Protocol
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Any, Dict, List

# MCP Server implementation
class AnsibleCollectionMCPServer:
    """MCP Server for Ansible Collection Management tools"""
    
    def __init__(self):
        self.tools_dir = Path(__file__).parent.parent / "scripts"
        
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return MCP tool definitions"""
        return [
            {
                "name": "ansible_analyze_collection",
                "description": "Analyze Ansible collection structure and complexity. Returns metrics on files, roles, playbooks, and complexity.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "collection_path": {
                            "type": "string",
                            "description": "Path to Ansible collection root directory"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["text", "json"],
                            "description": "Output format (default: text)",
                            "default": "text"
                        }
                    },
                    "required": ["collection_path"]
                }
            },
            {
                "name": "ansible_detect_antipatterns",
                "description": "Detect security vulnerabilities and anti-patterns in Ansible collection. Returns findings categorized by severity (CRITICAL, HIGH, MEDIUM, LOW).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "collection_path": {
                            "type": "string",
                            "description": "Path to Ansible collection root directory"
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                            "description": "Minimum severity level to report (optional)"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["text", "json"],
                            "description": "Output format (default: text)",
                            "default": "text"
                        }
                    },
                    "required": ["collection_path"]
                }
            },
            {
                "name": "ansible_consolidate_packages",
                "description": "Analyze package duplication across roles and generate consolidation plan. Identifies packages defined in multiple roles and recommends consolidation into common vars.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "collection_path": {
                            "type": "string",
                            "description": "Path to Ansible collection root directory"
                        },
                        "include_plan": {
                            "type": "boolean",
                            "description": "Include consolidation plan in output",
                            "default": False
                        },
                        "format": {
                            "type": "string",
                            "enum": ["text", "json"],
                            "description": "Output format (default: text)",
                            "default": "text"
                        }
                    },
                    "required": ["collection_path"]
                }
            },
            {
                "name": "ansible_analyze_variables",
                "description": "Analyze variable definitions and precedence across collection. Detects shadowing and traces variable usage. Can analyze all variables or a specific variable.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "collection_path": {
                            "type": "string",
                            "description": "Path to Ansible collection root directory"
                        },
                        "variable_name": {
                            "type": "string",
                            "description": "Specific variable to analyze (optional)"
                        },
                        "shadowed_only": {
                            "type": "boolean",
                            "description": "Show only shadowed variables",
                            "default": False
                        },
                        "format": {
                            "type": "string",
                            "enum": ["text", "json"],
                            "description": "Output format (default: text)",
                            "default": "text"
                        }
                    },
                    "required": ["collection_path"]
                }
            },
            {
                "name": "ansible_map_dependencies",
                "description": "Map role dependencies and generate dependency graphs. Detects circular dependencies, orphaned roles, and calculates dependency depth. Can generate Mermaid graphs.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "collection_path": {
                            "type": "string",
                            "description": "Path to Ansible collection root directory"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["text", "json", "mermaid"],
                            "description": "Output format (default: text)",
                            "default": "text"
                        },
                        "include_graph": {
                            "type": "boolean",
                            "description": "Include Mermaid graph in text output",
                            "default": False
                        }
                    },
                    "required": ["collection_path"]
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool and return results"""
        
        # Map tool names to scripts
        tool_script_map = {
            "ansible_analyze_collection": "collection_analyzer.py",
            "ansible_detect_antipatterns": "antipattern_detector.py",
            "ansible_consolidate_packages": "package_consolidator.py",
            "ansible_analyze_variables": "variable_analyzer.py",
            "ansible_map_dependencies": "role_mapper.py"
        }
        
        if tool_name not in tool_script_map:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]
            }
        
        script_name = tool_script_map[tool_name]
        script_path = self.tools_dir / script_name
        
        # Build command
        cmd = ["python3", str(script_path)]
        
        # Add collection path
        collection_path = arguments.get("collection_path")
        if not collection_path:
            return {
                "isError": True,
                "content": [{"type": "text", "text": "Missing required argument: collection_path"}]
            }
        cmd.append(collection_path)
        
        # Add format
        output_format = arguments.get("format", "text")
        cmd.extend(["--format", output_format])
        
        # Add tool-specific arguments
        if tool_name == "ansible_detect_antipatterns" and "severity" in arguments:
            cmd.extend(["--severity", arguments["severity"]])
        
        elif tool_name == "ansible_consolidate_packages" and arguments.get("include_plan"):
            cmd.append("--plan")
        
        elif tool_name == "ansible_analyze_variables":
            if "variable_name" in arguments:
                cmd.extend(["--variable", arguments["variable_name"]])
            if arguments.get("shadowed_only"):
                cmd.append("--shadowed-only")
        
        elif tool_name == "ansible_map_dependencies":
            if arguments.get("include_graph"):
                cmd.append("--graph")
        
        # Execute script
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                return {
                    "isError": True,
                    "content": [{
                        "type": "text",
                        "text": f"Tool execution failed: {result.stderr}"
                    }]
                }
            
            # Return result
            if output_format == "json":
                # Parse JSON and return structured
                try:
                    data = json.loads(result.stdout)
                    return {
                        "content": [{
                            "type": "text",
                            "text": json.dumps(data, indent=2)
                        }]
                    }
                except json.JSONDecodeError:
                    return {
                        "content": [{
                            "type": "text",
                            "text": result.stdout
                        }]
                    }
            else:
                # Return text output
                return {
                    "content": [{
                        "type": "text",
                        "text": result.stdout
                    }]
                }
        
        except subprocess.TimeoutExpired:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": "Tool execution timed out (>5 minutes)"
                }]
            }
        except Exception as e:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"Tool execution error: {str(e)}"
                }]
            }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol request"""
        method = request.get("method")
        
        if method == "tools/list":
            return {
                "tools": self.get_tool_definitions()
            }
        
        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            return self.execute_tool(tool_name, arguments)
        
        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }


def main():
    """Main MCP server loop"""
    server = AnsibleCollectionMCPServer()
    
    # MCP server uses JSON-RPC over stdio
    for line in sys.stdin:
        try:
            request = json.loads(line)
            response = server.handle_request(request)
            
            # Include request ID if present
            if "id" in request:
                response["id"] = request["id"]
            
            print(json.dumps(response), flush=True)
        
        except json.JSONDecodeError:
            error_response = {
                "error": {
                    "code": -32700,
                    "message": "Parse error: Invalid JSON"
                }
            }
            print(json.dumps(error_response), flush=True)
        
        except Exception as e:
            error_response = {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
