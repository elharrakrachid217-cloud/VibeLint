"""
core/remediator.py
==================
Takes code with known violations and applies automatic fixes.

This is VibeLint's superpower — we don't just flag problems,
we hand the developer a fixed version they can accept with one click.

Current auto-fixes:
- Replace hard-coded secrets with os.environ.get() calls
- Add .env template comments
- Flag auth issues with inline TODO comments (full AST rewrite is v2)

NOTE: The remediator is intentionally conservative.
We only auto-fix things we're 100% sure about.
For complex patterns (auth rewrites), we add a clear TODO comment
and let the developer make the change with guidance.
"""

import re

_HASH_COMMENT_LANGS = {"python", "ruby", "bash", "shell", "r", "elixir", "yaml", "terraform", "dockerfile"}
_SLASH_COMMENT_LANGS = {
    "javascript", "typescript", "java", "go", "php", "c", "cpp",
    "csharp", "rust", "kotlin", "swift", "scala", "lua",
}


def _comment_prefix(language: str) -> str:
    if language in _HASH_COMMENT_LANGS:
        return "#"
    if language in _SLASH_COMMENT_LANGS:
        return "//"
    if language == "html":
        return "<!--"
    return "#"


def _comment_suffix(language: str) -> str:
    if language == "html":
        return " -->"
    return ""


class Remediator:

    def fix(self, code: str, violations: list[dict], language: str) -> str:
        """
        Apply fixes for all violations and return the remediated code.
        """
        remediated = code

        for violation in violations:
            if violation["type"] == "hard_coded_secret":
                remediated = self._fix_secret(remediated, violation, language)
            elif violation["type"] == "insecure_auth":
                remediated = self._add_warning_comment(remediated, violation, language)
            elif violation["type"] == "injection_risk":
                remediated = self._add_warning_comment(remediated, violation, language)
            elif violation["type"] == "semgrep_finding":
                remediated = self._add_warning_comment(remediated, violation, language)

        return remediated

    def _fix_secret(self, code: str, violation: dict, language: str) -> str:
        """
        Replace hard-coded secrets with environment variable references.
        This is the one fix we can do automatically with high confidence.
        """
        offending_line = violation.get("offending_line", "")
        if not offending_line:
            return code

        lines = code.split('\n')
        fixed_lines = []

        for line in lines:
            if line.strip() == offending_line:
                fixed_line = self._replace_with_env_var(line, language)
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    _ENV_VAR_TEMPLATES: dict[str, str] = {
        "python":     '{indent}{var} = os.environ.get("{var}")  # secret moved to .env',
        "javascript": '{indent}const {var} = process.env.{var};  // secret moved to .env',
        "typescript": '{indent}const {var} = process.env.{var};  // secret moved to .env',
        "java":       '{indent}String {var} = System.getenv("{var}");  // secret moved to .env',
        "go":         '{indent}{var} := os.Getenv("{var}")  // secret moved to .env',
        "ruby":       "{indent}{var} = ENV['{var}']  # secret moved to .env",
        "php":        "{indent}${var} = getenv('{var}');  // secret moved to .env",
        "rust":       '{indent}let {var} = std::env::var("{var}").expect("{var} not set");  // secret moved to .env',
        "csharp":     '{indent}var {var} = Environment.GetEnvironmentVariable("{var}");  // secret moved to .env',
        "kotlin":     '{indent}val {var} = System.getenv("{var}")  // secret moved to .env',
        "swift":      '{indent}let {var} = ProcessInfo.processInfo.environment["{var}"]  // secret moved to .env',
        "scala":      '{indent}val {var} = sys.env.getOrElse("{var}", "")  // secret moved to .env',
    }

    def _replace_with_env_var(self, line: str, language: str) -> str:
        """
        Transform:   API_KEY = "sk-abc123..."
        Into:        API_KEY = os.environ.get("API_KEY")  # 🔍 VibeLint: secret moved to .env
        """
        cp = _comment_prefix(language)
        cs = _comment_suffix(language)
        match = re.match(r'(\s*)(\w+)\s*=\s*["\'].*["\']', line)
        if not match:
            indent = re.match(r'(\s*)', line).group(1)
            return (
                f"{indent}{cp} VIBELINT: Hard-coded secret removed. "
                f"Load from environment variable.{cs}"
            )

        indent = match.group(1)
        var_name = match.group(2).upper()

        template = self._ENV_VAR_TEMPLATES.get(language)
        if template:
            return template.format(indent=indent, var=var_name)

        return f"{indent}{cp} VIBELINT: Replace with env var for {var_name}{cs}"

    def _add_warning_comment(self, code: str, violation: dict, language: str) -> str:
        """
        For complex violations (auth, injection), inject a clear warning comment
        above the offending line with the fix hint.
        This is safer than attempting an automatic rewrite.
        """
        offending_line = violation.get("offending_line", "")
        if not offending_line:
            return code

        fix_hint = violation.get("fix_hint", "Review this line for security issues.")
        description = violation.get("description", "Security issue detected.")

        cp = _comment_prefix(language)
        cs = _comment_suffix(language)

        lines = code.split('\n')
        fixed_lines = []

        for line in lines:
            if line.strip() == offending_line:
                indent = re.match(r'(\s*)', line).group(1)
                fixed_lines.append(
                    f'{indent}{cp} VIBELINT [{violation["severity"].upper()}]: {description}{cs}'
                )
                fixed_lines.append(f'{indent}{cp} FIX: {fix_hint}{cs}')
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)
