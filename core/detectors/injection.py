"""
core/detectors/injection.py
===========================
Detects injection and traversal vulnerabilities in AI-generated code.

Covers:
- SQL injection (f-strings, .format(), %, concatenation)
- XSS (innerHTML, eval, document.write, dangerouslySetInnerHTML)
- Command injection (os.system, subprocess with shell=True)
- Path traversal (open() with user-controlled paths)
- Prototype pollution
"""

import re
from core.detectors.base import BaseDetector


class InjectionDetector(BaseDetector):

    INJECTION_PATTERNS = [
        # SQL built with f-strings — the #1 AI-generated vulnerability
        (
            r'(?i)(execute|query|cursor\.execute)\s*\(\s*f["\'].*SELECT|INSERT|UPDATE|DELETE',
            "SQL query built with an f-string allows injection. Use parameterized queries.",
            "critical"
        ),
        # SQL built with .format() or % formatting
        (
            r'(?i)(SELECT|INSERT|UPDATE|DELETE).*\.format\(',
            "SQL query built with .format() allows injection. Use parameterized queries.",
            "critical"
        ),
        (
            r'(?i)(SELECT|INSERT|UPDATE|DELETE).*%\s*[\(\{]',
            "SQL query built with % string formatting allows injection. Use parameterized queries.",
            "critical"
        ),
        # String concatenation in SQL (the classic)
        (
            r'(?i)(SELECT|INSERT|UPDATE|DELETE).*["\'\s]\s*\+\s*\w',
            "SQL query built with string concatenation allows injection. Use parameterized queries.",
            "critical"
        ),
        # Raw HTML rendering without escaping (XSS)
        (
            r'(?i)(innerHTML|outerHTML)\s*=.*\+',
            "User-controlled data inserted directly into DOM. Sanitize first to prevent XSS.",
            "high"
        ),
        # JS/TS: eval() with variable input (code injection)
        (
            r'eval\s*\(\s*[a-zA-Z_]',
            "eval() called with variable input allows arbitrary code execution. Never use eval() with dynamic data.",
            "critical"
        ),
        # JS/TS: document.write() with concatenation or template literals
        (
            r'document\.write\s*\(.*[\+\$]',
            "document.write() with dynamic data enables XSS. Use textContent or DOM APIs with proper escaping.",
            "high"
        ),
        # dangerouslySetInnerHTML in React without DOMPurify
        (
            r'dangerouslySetInnerHTML(?!.*DOMPurify)',
            "dangerouslySetInnerHTML used without DOMPurify. Sanitize with DOMPurify.sanitize() before rendering.",
            "high"
        ),
        # JS/TS: Prototype pollution via dynamic property assignment
        (
            r'(?i)\w+\[\s*(?:req|user|input|param|query|body|data)\w*\s*\]\s*=',
            "Dynamic property assignment with user-controlled key enables prototype pollution.",
            "high"
        ),
        # ── Command injection ──────────────────────────────────────────
        # os.system() with variable or f-string input
        (
            r'os\.system\s*\(\s*(?:f["\']|[a-zA-Z_])',
            "os.system() called with variable input enables command injection. "
            "Use subprocess.run() with a list of arguments instead.",
            "critical"
        ),
        # subprocess with shell=True
        (
            r'subprocess\.\w+\s*\(.*shell\s*=\s*True',
            "subprocess called with shell=True enables command injection. "
            "Pass arguments as a list without shell=True.",
            "critical"
        ),
        # ── Path traversal ─────────────────────────────────────────────
        # open() with user-controlled or dynamic path
        (
            r'open\s*\(\s*(?:f["\'].*\{|(?:req|user|input|param|query|body|data|request|args|filename|filepath|file_path|path|file_name)\w*)',
            "open() called with a user-controlled or dynamic path may allow path traversal. "
            "Resolve with os.path.realpath() and verify the result is under an allowed base directory.",
            "high"
        ),
    ]

    def detect(self, code: str, language: str) -> list[dict]:
        violations = []
        lines = code.split('\n')

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                continue

            for pattern, description, severity in self.INJECTION_PATTERNS:
                if re.search(pattern, line):
                    violations.append({
                        "type": "injection_risk",
                        "severity": severity,
                        "line": line_num,
                        "description": description,
                        "offending_line": line.strip(),
                        "fix_hint": self._get_fix_hint(language, description)
                    })
                    break

        return violations

    _SQL_FIX_HINTS: dict[str, str] = {
        "python": (
            "Replace string-built queries with parameterized queries. "
            "SQLAlchemy ORM example: db.query(User).filter(User.id == user_id). "
            "Raw psycopg2 example: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
        ),
        "javascript": (
            "Use an ORM like Prisma or Drizzle instead of raw SQL. "
            "If using raw queries: db.query('SELECT * FROM users WHERE id = $1', [userId]). "
            "For XSS: use DOMPurify — npm install dompurify."
        ),
        "typescript": (
            "Use an ORM like Prisma or Drizzle instead of raw SQL. "
            "If using raw queries: db.query('SELECT * FROM users WHERE id = $1', [userId]). "
            "For XSS: use DOMPurify — npm install dompurify."
        ),
        "java": (
            "Use PreparedStatement with parameterized queries: "
            "stmt = conn.prepareStatement(\"SELECT * FROM users WHERE id = ?\"); stmt.setInt(1, userId). "
            "Or use JPA/Hibernate with named parameters."
        ),
        "go": (
            "Use parameterized queries: db.Query(\"SELECT * FROM users WHERE id = $1\", userId). "
            "Never concatenate user input into SQL strings. Use sqlx or GORM for safer patterns."
        ),
        "ruby": (
            "Use ActiveRecord or parameterized queries: "
            "User.where(id: user_id) or conn.exec_params('SELECT * FROM users WHERE id = $1', [user_id]). "
            "Never interpolate user input into SQL strings."
        ),
        "php": (
            "Use PDO prepared statements: $stmt = $pdo->prepare('SELECT * FROM users WHERE id = ?'); "
            "$stmt->execute([$userId]). Never concatenate user input into SQL strings."
        ),
        "csharp": (
            "Use parameterized queries with SqlCommand: "
            "cmd.Parameters.AddWithValue(\"@id\", userId). "
            "Or use Entity Framework / Dapper with parameterized queries."
        ),
        "rust": (
            "Use parameterized queries with sqlx: "
            "sqlx::query(\"SELECT * FROM users WHERE id = $1\").bind(user_id). "
            "Never format! user input into SQL strings."
        ),
        "kotlin": (
            "Use PreparedStatement or Exposed ORM with parameterized queries. "
            "Never concatenate user input into SQL strings."
        ),
    }

    def _get_fix_hint(self, language: str, description: str = "") -> str:
        if language in ("javascript", "typescript"):
            if "eval()" in description:
                return (
                    "Remove eval() entirely. Use JSON.parse() for data, "
                    "or Function constructor with validated input if dynamic code is absolutely required. "
                    "Store configuration in process.env instead of evaluating dynamic strings."
                )
            if "document.write" in description:
                return (
                    "Replace document.write() with safe DOM APIs: "
                    "element.textContent for text, or createElement/appendChild for structure. "
                    "Never insert unsanitized user data into the DOM."
                )
            if "dangerouslySetInnerHTML" in description:
                return (
                    "Sanitize content before rendering: npm install dompurify, "
                    "then use dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(content) }}."
                )
            if "prototype pollution" in description.lower() or "dynamic property" in description.lower():
                return (
                    "Validate property keys against an allowlist before assignment. "
                    "Use Object.create(null) for lookup objects, or Map instead of plain objects. "
                    "Never use user input directly as an object key."
                )
        if language == "python":
            if "os.system" in description:
                return (
                    "Replace os.system() with subprocess.run(['cmd', 'arg1', 'arg2'], check=True). "
                    "Never pass user input into a shell command string."
                )
            if "shell=True" in description:
                return (
                    "Remove shell=True and pass arguments as a list: "
                    "subprocess.run(['cmd', 'arg1', 'arg2'], check=True). "
                    "If shell features are needed, validate and sanitize all input with shlex.quote()."
                )
            if "path traversal" in description.lower() or "open()" in description:
                return (
                    "Validate the file path before opening: "
                    "resolved = os.path.realpath(user_path); "
                    "assert resolved.startswith(ALLOWED_BASE_DIR). "
                    "Never pass raw user input to open()."
                )

        hint = self._SQL_FIX_HINTS.get(language)
        if hint:
            return hint
        return "Never build queries or HTML by concatenating user input. Use parameterized queries and output encoding."
