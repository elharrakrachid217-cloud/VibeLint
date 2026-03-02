# 🛡️ VibeGuard
### Security-First Coding Proxy for AI-Generated Code

VibeGuard intercepts AI-generated code **before it reaches your codebase** and automatically fixes:
- 🔑 Hard-coded secrets (API keys, tokens, database credentials)
- 🔐 Insecure authentication patterns (MD5 passwords, JWT without verification)
- 💉 SQL injection and XSS vulnerabilities

---

## Quick Start (5 minutes)

### 1. Clone and install dependencies

```bash
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
│   └── detectors/
│       ├── base.py            # Abstract base class for all detectors
│       ├── secrets.py         # Hard-coded secrets detector ← start here
│       ├── auth.py            # Insecure auth pattern detector
│       └── injection.py       # SQL injection + XSS detector
│
└── tests/
    └── test_scanner.py        # Test suite — run with: pytest tests/ -v
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
3. Add a test in `tests/test_scanner.py` first (test-driven development)
4. Run `pytest tests/ -v` to verify

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

## Roadmap

- [x] MCP server foundation
- [x] Secrets detection (regex-based)
- [x] Auth pattern detection
- [x] SQL injection + XSS detection
- [x] Auto-remediation engine
- [ ] Integrate Yelp's detect-secrets for broader coverage
- [ ] AST-based detection (more accurate than regex)
- [ ] JavaScript/TypeScript AST parser
- [ ] Web dashboard (React + FastAPI)
- [ ] Git pre-commit hook (free tier)
- [ ] VS Code extension
