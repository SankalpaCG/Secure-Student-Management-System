"""Fernet encryption for sensitive profile fields at rest."""

import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app


def _fernet_from_secret(secret: str) -> Fernet:
    """Derive a Fernet key from a secret string (legacy / dev fallback)."""
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
    return Fernet(key)


def _fernet_instances():
    """
    Return Fernet instances to try for decrypt (newest key first).

    Primary key: FIELD_ENCRYPTION_KEY environment variable.
    Fallback: SECRET_KEY-derived key for data encrypted before key migration.
    """
    instances = []
    env_key = os.environ.get("FIELD_ENCRYPTION_KEY") or current_app.config.get(
        "FIELD_ENCRYPTION_KEY"
    )
    if env_key:
        key = env_key.encode() if isinstance(env_key, str) else env_key
        instances.append(Fernet(key))
    secret = current_app.config.get("SECRET_KEY")
    if secret:
        instances.append(_fernet_from_secret(secret))
    return instances


def encrypt_value(value):
    """Encrypt a string for database storage. Uses FIELD_ENCRYPTION_KEY when set."""
    if not value:
        return None
    instances = _fernet_instances()
    if not instances:
        raise RuntimeError("FIELD_ENCRYPTION_KEY or SECRET_KEY required for encryption")
    return instances[0].encrypt(value.encode()).decode()


def decrypt_value(value):
    """Decrypt a stored value; supports legacy SECRET_KEY-encrypted data."""
    if not value:
        return None
    for fernet in _fernet_instances():
        try:
            return fernet.decrypt(value.encode()).decode()
        except (InvalidToken, ValueError):
            continue
    return value


# Backward-compatible aliases used across the application
encrypt_field = encrypt_value
decrypt_field = decrypt_value
