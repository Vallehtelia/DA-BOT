"""
Safe redaction utilities for logging sensitive information.
"""

import re
from typing import Any

_PATTERNS = [
    re.compile(r'(pass(?:word)?\s*[:=]\s*)([^\s,]+)', re.IGNORECASE),
    re.compile(r'(api[_-]?key\s*[:=]\s*)([^\s,]+)', re.IGNORECASE),
    re.compile(r'(secret\s*[:=]\s*)([^\s,]+)', re.IGNORECASE),
    re.compile(r'(token\s*[:=]\s*)([^\s,]+)', re.IGNORECASE),
    re.compile(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', re.IGNORECASE),
]

def safe_redact(obj: Any) -> Any:
    """Redact sensitive patterns in strings; works recursively on lists/dicts."""
    if obj is None:
        return obj
    if isinstance(obj, str):
        s = obj
        # Apply replacements; keep group 1 (label) and redact group 2 (value)
        s = _PATTERNS[0].sub(r'\1[REDACTED]', s)
        s = _PATTERNS[1].sub(r'\1[REDACTED]', s)
        s = _PATTERNS[2].sub(r'\1[REDACTED]', s)
        s = _PATTERNS[3].sub(r'\1[REDACTED]', s)
        # emails fully redacted
        s = _PATTERNS[4].sub('[REDACTED_EMAIL]', s)
        return s
    if isinstance(obj, dict):
        return {k: safe_redact(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [safe_redact(x) for x in obj]
    return obj
