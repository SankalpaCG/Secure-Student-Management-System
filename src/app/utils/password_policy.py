"""Strong password policy (OWASP-aligned)."""

import re

MIN_LENGTH = 10

_REQUIREMENTS = (
    (re.compile(r"[A-Z]"), "at least one uppercase letter"),
    (re.compile(r"[a-z]"), "at least one lowercase letter"),
    (re.compile(r"\d"), "at least one number"),
    (re.compile(r"[^A-Za-z0-9]"), "at least one special character"),
)


def validate_password_strength(password: str) -> list[str]:
    """
    Return a list of human-readable errors; empty list means password is acceptable.
    """
    if not password:
        return ["Password is required."]
    errors = []
    if len(password) < MIN_LENGTH:
        errors.append(f"Password must be at least {MIN_LENGTH} characters long.")
    for pattern, message in _REQUIREMENTS:
        if not pattern.search(password):
            errors.append(f"Password must contain {message}.")
    return errors


def password_policy_summary() -> str:
    return (
        f"Minimum {MIN_LENGTH} characters with uppercase, lowercase, "
        "a number, and a special character."
    )
