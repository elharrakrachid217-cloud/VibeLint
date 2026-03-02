"""
core/detectors/injection.py
===========================
Detects SQL injection and XSS vulnerabilities in AI-generated code.

AI agents frequently build SQL queries with string concatenation
because it 'works' in demos. It's catastrophically dangerous in production.

Patterns we catch:
- SQL queries built with f-strings or string concatenation
- Raw user input inserted into queries
- Missing input sanitization before rendering HTML

TODO for you to expand:
- Command injection (os.system with user input)
- Path traversal vulnerabilities
- SSRF (Server Side Request Forgery) patterns
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
            return (
                "Use an ORM like Prisma or Drizzle instead of raw SQL. "
                "If using raw queries: db.query('SELECT * FROM users WHERE id = $1', [userId]). "
                "For XSS: use DOMPurify — npm install dompurify."
            )
        if language == "python":
            return (
                "Replace string-built queries with parameterized queries. "
                "SQLAlchemy ORM example: db.query(User).filter(User.id == user_id). "
                "Raw psycopg2 example: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
            )
        return "Never build queries or HTML by concatenating user input. Use parameterized queries and output encoding."
