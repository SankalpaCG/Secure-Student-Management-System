"""XSS mitigation: strip HTML and dangerous content from user input."""

import bleach

# Allow no HTML tags in stored user text (Jinja auto-escapes on output).
ALLOWED_TAGS: list[str] = []
ALLOWED_ATTRIBUTES: dict[str, list[str]] = {}


def sanitize_text(value, max_length=None):
    """
    Sanitize user-provided text before database storage.

    Uses Bleach to remove script tags and HTML. Template output remains
    auto-escaped by Jinja2; never use |safe on user-controlled data.
    """
    if value is None:
        return None
    cleaned = bleach.clean(
        str(value).strip(),
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    return cleaned or None
