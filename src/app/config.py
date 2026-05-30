import os
from datetime import timedelta


def _build_database_uri():
    """Build a MySQL URI from individual environment variables."""
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "3306")
    name = os.environ.get("DB_NAME")

    if not all([user, password, name]):
        return None

    return (
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
        "?charset=utf8mb4"
    )


def _is_production():
    return os.environ.get("FLASK_ENV", "development").lower() == "production"


# Content-Security-Policy: allow Bootstrap/Chart.js CDNs used in templates.
_DEFAULT_CSP = (
    "default-src 'self'; "
    "script-src 'self' https://cdn.jsdelivr.net; "
    "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self' https://cdn.jsdelivr.net; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; "
    "base-uri 'self'; "
    "form-action 'self'"
)


class Config:
    """Base application configuration loaded from environment variables."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    # CSRF (Flask-WTF) — enabled globally; all POST forms must include csrf_token.
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # Field-level encryption (Fernet)
    FIELD_ENCRYPTION_KEY = os.environ.get("FIELD_ENCRYPTION_KEY")

    # Session security
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.environ.get("SESSION_TIMEOUT_HOURS", "2"))
    )
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = _is_production()

    # Rate limiting (Flask-Limiter)
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_HEADERS_ENABLED = True
    LOGIN_RATE_LIMIT = os.environ.get("LOGIN_RATE_LIMIT", "5 per minute")
    TWO_FACTOR_RATE_LIMIT = os.environ.get("TWO_FACTOR_RATE_LIMIT", "5 per minute")
    API_LOGIN_RATE_LIMIT = os.environ.get("API_LOGIN_RATE_LIMIT", "10 per minute")
    PROFILE_UPDATE_RATE_LIMIT = os.environ.get("PROFILE_UPDATE_RATE_LIMIT", "10 per hour")
    ENROLLMENT_RATE_LIMIT = os.environ.get("ENROLLMENT_RATE_LIMIT", "20 per hour")
    API_REFRESH_RATE_LIMIT = os.environ.get("API_REFRESH_RATE_LIMIT", "30 per minute")

    # JWT API
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or SECRET_KEY
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_EXPIRE_MINUTES", "15"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get("JWT_REFRESH_EXPIRE_DAYS", "7"))
    )

    # HTTP security headers
    CONTENT_SECURITY_POLICY = os.environ.get("CONTENT_SECURITY_POLICY", _DEFAULT_CSP)

    TOTP_ISSUER_NAME = os.environ.get("TOTP_ISSUER_NAME", "Secure Student MS")
    RECOVERY_CODE_COUNT = int(os.environ.get("RECOVERY_CODE_COUNT", "10"))
