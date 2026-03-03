# Install VibeLint

VibeLint is an MCP server that scans AI-generated code for security issues before it reaches your files.

> **Easiest way to install:** Copy the content of this file and give it to your AI agent (Cursor, Claude Code, Windsurf, Antigravity, etc.) with the message: *"Install this MCP for me."* It will handle everything below.

---

## Before you start

You need **Python 3.8 or newer** installed on your machine. To check, open a terminal and run:

```
python --version
```

If you don't have Python, download it from [python.org](https://www.python.org/downloads/).

## Step 1 — Clone and install

```
git clone https://github.com/elharrakrachid217-cloud/vibelint.git
cd vibelint
pip install -r requirements.txt
```

## Step 2 — Run the auto-installer

```
python install_mcp.py
```

This will auto-detect your IDE (Cursor, Windsurf, or Claude Desktop), resolve the correct Python path and server path, and write the config for you.

To target a specific IDE:

```
python install_mcp.py --ide cursor
python install_mcp.py --ide windsurf
python install_mcp.py --ide claude
```

## Step 3 — Restart your IDE

Reload or restart your IDE so it picks up the new MCP server. Done.

In Cursor: go to **Settings > MCP** and click the restart button next to vibelint.

---

## Manual setup (if you prefer)

Open your IDE's MCP configuration file and add this, replacing both paths with the **real absolute paths** on your machine:

```json
{
  "mcpServers": {
    "vibelint": {
      "command": "/absolute/path/to/python",
      "args": ["/absolute/path/to/vibelint/server.py"]
    }
  }
}
```

**Important:** Use full absolute paths for both `command` and `args`. Do **not** rely on `cwd` — some IDEs ignore it.

| OS | Example |
|----|---------|
| Windows | `"command": "C:\\Users\\you\\AppData\\Local\\Programs\\Python\\Python312\\python.exe"` |
| macOS | `"command": "/usr/local/bin/python3"` |
| Linux | `"command": "/usr/bin/python3"` |

---

## Verify (optional)

Run this inside the `vibelint` folder:

```
python server.py
```

If you see `VibeLint — AI Code Security Scanner` — everything is working. You can close it; your IDE starts the server on its own.
