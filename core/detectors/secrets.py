"""
core/detectors/secrets.py
=========================
Detects hard-coded secrets in AI-generated code.

This is Violation Type #1 — the most common issue in vibe coding.
AI agents love to hard-code API keys directly into source files.

Patterns we catch:
- API keys (OpenAI, Anthropic, AWS, Stripe, etc.)
- Database connection strings with credentials
- Hard-coded passwords in variable assignments
- JWT secrets and OAuth tokens

TODO for you to expand:
- Add more vendor-specific key patterns (Twilio, SendGrid, GitHub tokens)
- Integrate Yelp's detect-secrets library for even broader coverage
  (pip install detect-secrets) — it has 30+ built-in patterns
"""

import re
from core.detectors.base import BaseDetector


class SecretsDetector(BaseDetector):

    # Patterns that indicate a secret is hard-coded
    # Each tuple: (pattern, description, severity)
    SECRET_PATTERNS = [
        # Generic high-entropy strings assigned to key-sounding variables
        (
            r'(?i)(api_key|apikey|api_secret|secret_key|private_key|access_token|auth_token|jwt_secret)\s*=\s*["\']([A-Za-z0-9+/\-_]{20,})["\']',
            "Hard-coded API key or secret token detected",
            "critical"
        ),
        # OpenAI / Anthropic keys (very common in vibe coding)
        (
            r'sk-[A-Za-z0-9]{20,}',
            "Hard-coded OpenAI API key detected (sk-...)",
            "critical"
        ),
        (
            r'sk-ant-[A-Za-z0-9\-]{20,}',
            "Hard-coded Anthropic API key detected",
            "critical"
        ),
        # AWS credentials
        (
            r'AKIA[0-9A-Z]{16}',
            "Hard-coded AWS Access Key ID detected",
            "critical"
        ),
        (
            r'(?i)aws_secret_access_key\s*=\s*["\'][A-Za-z0-9+/]{40}["\']',
            "Hard-coded AWS Secret Access Key detected",
            "critical"
        ),
        # Database URLs with credentials embedded
        (
            r'(?i)(postgres|mysql|mongodb|redis):\/\/[^:]+:[^@]+@',
            "Database connection string contains hard-coded credentials",
            "critical"
        ),
        # Hard-coded passwords
        (
            r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{6,}["\']',
            "Hard-coded password detected in source code",
            "high"
        ),
        # Stripe keys
        (
            r'(?i)(sk_live|sk_test|pk_live|pk_test)_[A-Za-z0-9]{24,}',
            "Hard-coded Stripe API key detected",
            "critical"
        ),
    ]

    def detect(self, code: str, language: str) -> list[dict]:
        violations = []
        lines = code.split('\n')

        for line_num, line in enumerate(lines, start=1):
            # Skip comment lines — not actual code
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                continue

            # Skip .env.example style files (these are safe templates)
            if 'YOUR_KEY_HERE' in line or 'your_key_here' in line:
                continue

            for pattern, description, severity in self.SECRET_PATTERNS:
                if re.search(pattern, line):
                    violations.append({
                        "type": "hard_coded_secret",
                        "severity": severity,
                        "line": line_num,
                        "description": description,
                        "offending_line": line.strip(),
                        "fix_hint": self._get_fix_hint(pattern, line, language)
                    })
                    break  # One violation per line is enough

        return violations

    def _get_fix_hint(self, pattern: str, line: str, language: str) -> str:
        """Return a specific, actionable fix instruction for the violation."""

        if language == "python":
            return (
                "Remove this hard-coded value. "
                "Add it to a .env file and load it with: "
                "import os; value = os.environ.get('YOUR_VAR_NAME'). "
                "Make sure .env is in your .gitignore."
            )
        elif language in ("javascript", "typescript"):
            return (
                "Remove this hard-coded value. "
                "Add it to a .env file and access it with: "
                "process.env.YOUR_VAR_NAME. "
                "Install dotenv: npm install dotenv, then add require('dotenv').config() at the top."
            )
        return "Move this value to an environment variable and never commit it to source control."
