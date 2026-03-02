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

### 3. Connect to Cursor

Open `.cursor/mcp.json` and replace the `cwd` path with the **absolute path** to this folder.

**Mac/Linux example:**
```json
"cwd": "/Users/yourname/projects/vibeguard"
```

**Windows example:**
```json
"cwd": "C:\\Users\\yourname\\projects\\vibeguard"
```

Then in Cursor: `Settings → MCP → Add Server` and point it to this config file.

### 4. Start the server

```bash
python server.py
```

You should see:
```
🛡️  VibeGuard MCP Server starting...
   Waiting for Cursor to connect...
```

---

## How It Works

```
You describe a feature in Cursor
        ↓
Claude (Opus 4.6) generates code
        ↓
Cursor calls VibeGuard's security_check tool
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
├── server.py                  # MCP server — entry point, this is what Cursor connects to
├── requirements.txt
├── .cursor/
│   └── mcp.json               # Cursor MCP configuration
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
