import base64
import hashlib
import io
import secrets

import pyotp
import qrcode
from cryptography.fernet import Fernet, InvalidToken
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash


def _fernet():
    key = base64.urlsafe_b64encode(
        hashlib.sha256(current_app.config["SECRET_KEY"].encode()).digest()
    )
    return Fernet(key)


def generate_totp_secret():
    """Generate a new base32 TOTP secret."""
    return pyotp.random_base32()


def encrypt_totp_secret(secret):
    """Encrypt a TOTP secret for database storage."""
    return _fernet().encrypt(secret.encode()).decode()


def decrypt_totp_secret(encrypted_secret):
    """Decrypt a stored TOTP secret."""
    if not encrypted_secret:
        return None
    try:
        return _fernet().decrypt(encrypted_secret.encode()).decode()
    except InvalidToken:
        return None


def build_provisioning_uri(secret, email):
    """Build an otpauth:// URI for authenticator apps."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=current_app.config["TOTP_ISSUER_NAME"])


def generate_qr_code_base64(provisioning_uri):
    """Return a base64-encoded PNG QR code for the provisioning URI."""
    image = qrcode.make(provisioning_uri)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def verify_totp_code(encrypted_secret, code):
    """Verify a 6-digit TOTP code against an encrypted secret."""
    secret = decrypt_totp_secret(encrypted_secret)
    if not secret:
        return False
    totp = pyotp.TOTP(secret)
    return totp.verify(code.strip(), valid_window=1)


def generate_recovery_codes(count=None):
    """Generate human-readable single-use recovery codes."""
    count = count or current_app.config.get("RECOVERY_CODE_COUNT", 10)
    codes = []
    for _ in range(count):
        part1 = secrets.token_hex(2).upper()
        part2 = secrets.token_hex(2).upper()
        codes.append(f"{part1}-{part2}")
    return codes


def normalize_recovery_code(code):
    return code.replace("-", "").replace(" ", "").upper()


def hash_recovery_code(code):
    return generate_password_hash(normalize_recovery_code(code), method="pbkdf2:sha256")


def verify_recovery_code_hash(code_hash, code):
    return check_password_hash(code_hash, normalize_recovery_code(code))
