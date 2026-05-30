"""Password hashing and verification (no plaintext logging)."""

from werkzeug.security import check_password_hash, generate_password_hash

from app.utils.password_policy import validate_password_strength

# PBKDF2-SHA256 with 600k iterations (Werkzeug 3.x default method family).
_HASH_METHOD = "pbkdf2:sha256:600000"


def hash_password(password: str) -> str:
    """Hash a plaintext password; never log or persist the plaintext."""
    return generate_password_hash(password, method=_HASH_METHOD, salt_length=16)


def verify_password(password_hash: str, password: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    if not password_hash or not password:
        return False
    return check_password_hash(password_hash, password)


def assert_password_policy(password: str) -> None:
    """Raise ValueError with combined message if password fails policy."""
    errors = validate_password_strength(password)
    if errors:
        raise ValueError(" ".join(errors))
