"""
VibeGuard MCP Server
====================
This is the main entry point. Any MCP-compatible IDE or AI agent calls this
server before writing AI-generated code to disk. We scan it, flag violations,
and return fixes.

Run with:
    python server.py
"""

import asyncio
import json
import sys
import os
import io

# Ensure imports work regardless of which directory the MCP client launches from
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from core.scanner import SecurityScanner

# Initialize the server and scanner
app = Server(
    "vibeguard",
    instructions=(
        "VibeGuard is a MANDATORY security gate for all code generation. "
        "You MUST call the security_check tool with the complete code contents "
        "BEFORE every file-write operation — this includes using Write, StrReplace, "
        "creating new files, or any shell command that writes code. "
        "If security_check returns violations, use the remediated code it provides "
        "instead of your original. NEVER write, save, or apply code to disk without "
        "scanning it through security_check first. This applies to EVERY code change, "
        "regardless of size or perceived risk."
    ),
)
scanner = SecurityScanner()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Expose the security_check tool as a mandatory pre-write gate."""
    return [
        Tool(
            name="security_check",
            description=(
                "REQUIRED pre-write security gate — you MUST call this tool on every code block "
                "BEFORE writing or saving any file to disk. Never skip it, even for small edits. "
                "Submit the full code you intend to write; use the returned remediated code in place "
                "of your original if violations are found. "
                "Detects: hard-coded secrets, weak authentication, SQL injection, and other vulnerabilities. "
                "Returns pass/fail status, violation details with severity, and auto-fixed code."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": (
                            "The complete code you are about to write to disk. "
                            "Include ALL code exactly as you plan to save it — do not omit sections."
                        )
                    },
                    "filename": {
                        "type": "string",
                        "description": (
                            "Target filename including extension (e.g., 'auth.py', 'db.js', 'api.ts'). "
                            "Used to select language-specific security rules."
                        )
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language of the code block.",
                        "enum": ["python", "javascript", "typescript"]
                    }
                },
                "required": ["code", "filename", "language"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Route incoming tool calls to the security scanner."""
    if name != "security_check":
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    code = arguments.get("code", "")
    filename = arguments.get("filename", "unknown")
    language = arguments.get("language", "python")

    # Run the security scan
    result = scanner.scan(code=code, filename=filename, language=language)

    # Format and return the result
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    print("🛡️  VibeGuard MCP Server starting...")
    print("   Waiting for MCP client to connect...\n")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    asyncio.run(main())
