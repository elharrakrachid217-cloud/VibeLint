# 🛡️ VibeGuard

![Tests](https://img.shields.io/badge/tests-65%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Every time an AI writes code for you, it might be leaking your API keys, breaking your auth, or opening your database to injection attacks. **VibeGuard catches it before it ever touches your files.**

- 🔑 Hard-coded secrets (API keys, tokens, database credentials, `process.env` fallback bypasses, Next.js secrets)
- 🔐 Insecure authentication patterns (MD5 passwords, JWT without verification, localStorage JWT storage, NextAuth misconfigs)
- 💉 SQL injection, XSS, and JS/TS-specific risks (`eval()`, `document.write()`, `dangerouslySetInnerHTML`, prototype pollution)

---

## Quick Start (5 minutes)

### 1. Clone and install dependencies

```bash
git clone https://github.com/elharrakrachid217-cloud/vibeguard.git
cd vibeguard
pip install -r requirements.txt
```

### 2. Run the test suite to verify everything works

```bash
pytest tests/ -v
```

All tests should pass. If they do — your scanner is working.

### 3. Connect to your IDE / AI agent

VibeGuard uses the **Model Context Protocol (MCP)** standard and works with any MCP-compatible client — Cursor, Windsurf, Claude Desktop, VS Code (Copilot), and others.

Create or edit your IDE's MCP configuration file and add a `vibeguard` entry. The typical config looks like:

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

Replace the `cwd` value with the **absolute path** to this folder:

**Mac/Linux example:**
```json
"cwd": "/Users/yourname/projects/vibeguard"
```

**Windows example:**
```json
"cwd": "C:\\Users\\yourname\\projects\\vibeguard"
```

Where this config file lives depends on your IDE:

| IDE / Client | Config location |
|---|---|
| **Cursor** | `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global) |
| **Windsurf** | `.windsurf/mcp.json` (project) or `~/.codeium/windsurf/mcp_config.json` (global) |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows) |
| **VS Code (Copilot)** | `.vscode/mcp.json` (project) |

After adding the config, restart your IDE or reload the window so it picks up the new MCP server.

### 4. Start the server

```bash
python server.py
```

You should see:
```
🛡️  VibeGuard MCP Server starting...
   Waiting for MCP client to connect...
```

---

## Installation as Background Service

You can register VibeGuard to start automatically when you log in.
The installer auto-detects your OS and uses the native service mechanism.

### Install

```bash
python install_service.py
```

**What happens on each OS:**

| OS | Mechanism | Service file location |
|---|---|---|
| **Windows** | Task Scheduler (`schtasks`) | Visible in Task Scheduler as "VibeGuard" |
| **macOS** | launchd (plist) | `~/Library/LaunchAgents/com.vibeguard.server.plist` |
| **Linux** | systemd (user unit) | `~/.config/systemd/user/vibeguard.service` |

You should see output like:

```
🛡️  VibeGuard Service Installer
  Python:  /usr/bin/python3
  Server:  /home/you/vibeguard/server.py

🐧  Detected: Linux
  Installing via systemd (user service) …

  ✓ Log directory: /home/you/vibeguard/logs
  ✓ Made executable: server.py
  ✓ Unit file written: /home/you/.config/systemd/user/vibeguard.service
  ✓ Service enabled (auto-starts at login)
  ✓ Service started — VibeGuard is running

  Done! VibeGuard will auto-start on next login.
```

Logs are written to `vibeguard/logs/vibeguard.log`.

### Uninstall

```bash
python uninstall_service.py
```

This stops the service, removes the registration, and cleans up generated files.
Log files in `logs/` are preserved.

### Troubleshooting

- **Windows "Access is denied"** — right-click your terminal and choose "Run as administrator", then re-run `python install_service.py`.
- **macOS/Linux permission errors** — check that `~/Library/LaunchAgents/` (Mac) or `~/.config/systemd/user/` (Linux) is writable by your user.
- **Service registered but not running** — check `logs/vibeguard.log` for errors. The most common cause is a missing dependency (`pip install -r requirements.txt`).

---

## How It Works

```
You describe a feature in your IDE
        ↓
The AI agent generates code
        ↓
Your IDE calls VibeGuard's security_check tool via MCP
        ↓
VibeGuard scans for secrets, insecure auth, injection risks
        ↓
Returns: approved ✅ or violations 🚨 + auto-fixed code
        ↓
You review and accept the clean version
```

---

## Project Structure

```
vibeguard/
├── server.py                  # MCP server — entry point, this is what your IDE connects to
├── requirements.txt
├── .cursor/
│   └── mcp.json               # MCP configuration (Cursor example — adapt for your IDE)
│
├── core/
│   ├── scanner.py             # Orchestrates all detectors and returns final result
│   ├── remediator.py          # Auto-fixes violations in the code
│   ├── logger.py              # SQLite-backed audit log for scan results
│   └── detectors/
│       ├── base.py            # Abstract base class for all detectors
│       ├── secrets.py         # Hard-coded secrets detector (Python + JS/TS)
│       ├── auth.py            # Insecure auth pattern detector (Python + JS/TS)
│       └── injection.py       # SQL injection, XSS, and JS/TS injection detector
│
└── tests/
    ├── test_scanner.py        # Core scanner tests (16 tests)
    ├── test_scanner_js.py     # JS/TS-specific pattern tests (27 tests)
    └── test_logger.py         # Audit logger tests (22 tests)
```

---

## Adding a New Detection Pattern

1. Open the relevant detector in `core/detectors/`
2. Add a new tuple to the `*_PATTERNS` list:
   ```python
   (
       r'your_regex_pattern_here',
       "Human-readable description of the vulnerability",
       "critical"  # or "high", "medium", "low"
   ),
   ```
3. Add a test first — use `tests/test_scanner.py` for Python patterns or `tests/test_scanner_js.py` for JS/TS patterns
4. Run `pytest tests/ -v` to verify (65 tests should pass)

That's it. No other files need to change.

---

## Testing Your Scanner Manually

You can test the scanner directly from Python:

```python
from core.scanner import SecurityScanner

scanner = SecurityScanner()
result = scanner.scan(
    code='api_key = "sk-abc123verylongkey"',
    filename="app.py",
    language="python"
)
print(result["summary"])
print(result["remediated_code"])
```

---

## JS/TS Detection Coverage

| Category | Pattern | Severity |
|----------|---------|----------|
| **Secrets** | `process.env.KEY \|\| "fallback"` bypass | high |
| **Secrets** | Hardcoded `NEXTAUTH_SECRET` / `NEXTAUTH_URL` | critical |
| **Secrets** | `NEXT_PUBLIC_*` variables hardcoded inline | high |
| **Auth** | `localStorage.setItem("token", ...)` | high |
| **Auth** | `fetch()` with credentials in URL params | high |
| **Auth** | `NextAuth({ debug: true })` in production | high |
| **Injection** | `eval(variable)` with dynamic input | critical |
| **Injection** | `document.write()` with user data | high |
| **Injection** | `dangerouslySetInnerHTML` without DOMPurify | high |
| **Injection** | `obj[userInput] = value` prototype pollution | high |

All fix hints for JS/TS use `process.env.VARIABLE_NAME` syntax, not Python's `os.environ`.

---

## Roadmap

- [x] MCP server foundation
- [x] Secrets detection (regex-based)
- [x] Auth pattern detection
- [x] SQL injection + XSS detection
- [x] Auto-remediation engine
- [x] JavaScript/TypeScript pattern detection (10 new patterns)
- [x] SQLite audit logger
- [ ] Integrate Yelp's detect-secrets for broader coverage
- [ ] AST-based detection (more accurate than regex)
- [ ] JavaScript/TypeScript AST parser
- [ ] Web dashboard (React + FastAPI)
- [ ] Git pre-commit hook (free tier)
- [ ] VS Code extension
