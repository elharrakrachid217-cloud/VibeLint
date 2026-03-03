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
git clone https://github.com/elharrakrachid217-cloud/VibeLint.git
cd VibeLint
pip install -r requirements.txt
```

## Step 2 — Add to your MCP config

Open your IDE's MCP configuration file and add this:

```json
{
  "mcpServers": {
    "vibelint": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/vibelint"
    }
  }
}
```

Replace `/absolute/path/to/vibelint` with the real path to the folder you just cloned.

## Step 3 — Restart your IDE

Reload or restart your IDE so it picks up the new MCP server. Done.

---

## Verify (optional)

Run this inside the `vibelint` folder:

```
python server.py
```

If you see `VibeLint MCP Server starting...` — everything is working. You can close it; your IDE starts the server on its own.
