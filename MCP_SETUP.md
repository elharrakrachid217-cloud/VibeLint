# VibeGuard MCP — Setup Guide

VibeGuard works with any IDE or AI agent that supports the **Model Context Protocol (MCP)**. Below are setup instructions for common clients.

---

## Cursor

### Method 1: Project config (recommended)

1. **Open the correct folder in Cursor**
   - File → Open Folder
   - Choose: `vibeguard_starter` (the parent folder that contains the `vibeguard` subfolder)
   - Cursor looks for `.cursor/mcp.json` in the folder you open.

2. **Reload so Cursor sees the config**
   - `Ctrl+Shift+P` → run **"Developer: Reload Window"**
   - Or close Cursor and open the folder again.

3. **Check MCP**
   - `Ctrl+Shift+P` → **"Cursor: Open MCP Servers"** (or **Settings → Cursor Settings → Features → MCP**)
   - You should see **vibeguard** in the list. Toggle it on if needed.

### Method 2: Cursor Settings UI

1. Open **Cursor Settings** → **Features** (or **Tools & MCP**) → **MCP**.
2. Click **"+ Add new MCP server"**.
3. Enter:
   - **Name:** `vibeguard`
   - **Type:** Command
   - **Command:** `python`
   - **Arguments:** `server.py`
   - **Working directory (cwd):** absolute path to the `vibeguard` folder
4. Save and restart Cursor.

### Method 3: Global config (all projects)

Edit `C:\Users\<you>\.cursor\mcp.json` (or `%APPDATA%\Cursor\mcp.json`) and add the `vibeguard` server block. Restart Cursor.

---

## Windsurf

1. Create or edit `.windsurf/mcp.json` in your project root (or the global config at `~/.codeium/windsurf/mcp_config.json`).
2. Add:
   ```json
   {
     "mcpServers": {
       "vibeguard": {
         "command": "python",
         "args": ["server.py"],
         "cwd": "/absolute/path/to/vibeguard"
       }
     }
   }
   ```
3. Restart Windsurf.

---

## Claude Desktop

1. Open the config file:
   - **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the `vibeguard` server block (same JSON as above).
3. Restart Claude Desktop.

---

## VS Code (GitHub Copilot)

1. Create or edit `.vscode/mcp.json` in your project root.
2. Add the same `mcpServers.vibeguard` JSON block.
3. Reload VS Code.

---

## Any other MCP-compatible client

The pattern is always the same:

```json
{
  "mcpServers": {
    "vibeguard": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/vibeguard"
    }
  }
}
```

Point `cwd` to the folder containing `server.py`, add this to your client's MCP config, and restart.

---

## Troubleshooting

- **Python on PATH**
  Run `python --version` in a new terminal. If it fails, use the full path to `python.exe` in the `command` field.

- **Paths with spaces**
  If your path contains spaces, make sure the `cwd` value is properly quoted in JSON (e.g. `"C:\\Users\\me\\my project\\vibeguard"`).

- **Verify the server can start**
  Run `python server.py` from the `vibeguard` folder. You should see:
  ```
  🛡️  VibeGuard MCP Server starting...
     Waiting for MCP client to connect...
  ```
  If that works, the problem is in your IDE's MCP config — double-check the path.
