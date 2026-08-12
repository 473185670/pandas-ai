"""
Code validation utilities.

Validates LLM-generated Python code before returning it to the user:
1. Extracts the code block from the LLM response.
2. Syntax-checks it with `ast.parse` (catches syntax errors without running).
3. Flags dangerous operations (subprocess, eval, exec, os.remove, etc.).
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass


# Patterns that should never appear in generated code
DANGEROUS_NAMES = {
    "eval", "exec", "compile", "__import__",
    "system", "popen", "remove", "rmdir", "unlink", "kill",
}
DANGEROUS_MODULES = {"subprocess", "shutil", "os", "sys"}


@dataclass
class ValidationResult:
    code: str
    is_valid: bool
    syntax_error: str = ""
    safety_warnings: list[str] = None

    def __post_init__(self):
        if self.safety_warnings is None:
            self.safety_warnings = []


_CODE_BLOCK_RE = re.compile(r"```python\s*\n(.*?)```", re.DOTALL)
_CODE_BLOCK_GENERIC_RE = re.compile(r"```\s*\n(.*?)```", re.DOTALL)


def extract_code(raw: str) -> str:
    """Pull the first Python code block out of an LLM response."""
    if m := _CODE_BLOCK_RE.search(raw):
        return m.group(1).strip()
    if m := _CODE_BLOCK_GENERIC_RE.search(raw):
        return m.group(1).strip()
    # No fence — if it already looks like code, return as-is
    stripped = raw.strip()
    if stripped.startswith(("import ", "from ", "df", "print")) or "=" in stripped.split("\n")[0]:
        return stripped
    return stripped


def check_safety(code: str) -> list[str]:
    """Return a list of safety warnings (empty = safe)."""
    warnings: list[str] = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ["unable to parse code for safety check"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in DANGEROUS_NAMES:
                warnings.append(f"calls dangerous function '{func.id}'")
            if isinstance(func, ast.Attribute) and func.attr in DANGEROUS_NAMES:
                warnings.append(f"calls dangerous method '.{func.attr}'")
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in DANGEROUS_MODULES:
                    warnings.append(f"imports '{alias.name}'")
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in DANGEROUS_MODULES:
                warnings.append(f"imports from '{node.module}'")
    return warnings


def validate(raw_llm_response: str) -> ValidationResult:
    """Full validation pipeline: extract → syntax check → safety check."""
    code = extract_code(raw_llm_response)

    # Syntax check
    try:
        ast.parse(code)
        is_valid = True
        syntax_error = ""
    except SyntaxError as e:
        is_valid = False
        syntax_error = f"line {e.lineno}: {e.msg}"

    warnings = check_safety(code) if is_valid else []
    return ValidationResult(
        code=code,
        is_valid=is_valid,
        syntax_error=syntax_error,
        safety_warnings=warnings,
    )


if __name__ == "__main__":
    # Smoke tests
    ok = validate("```python\ndf.groupby('a')['b'].sum()\n```")
    print("Valid:", ok.is_valid, "| code:", ok.code)

    bad = validate("```python\nimport os\nos.system('rm -rf /')\n```")
    print("Valid:", bad.is_valid, "| warnings:", bad.safety_warnings)

    syn = validate("```python\ndf.groupby('a'[)\n```")
    print("Valid:", syn.is_valid, "| error:", syn.syntax_error)
