"""
SQL injection prevention documentation and helpers.

This application uses SQLAlchemy ORM exclusively for application queries.
User input is never concatenated into SQL strings. The ORM binds parameters
automatically, which mitigates SQL injection (OWASP A03:2021 Injection).

Example (safe):
    User.query.filter_by(email=user_supplied_email).first()

Example (unsafe — do not use):
    db.session.execute(f"SELECT * FROM users WHERE email = '{email}'")

If raw SQL is ever required, use:
    db.session.execute(text("SELECT ... WHERE id = :id"), {"id": user_id})
"""


from sqlalchemy import text

from app.extensions import db


def execute_parameterized(sql: str, params: dict):
    """
    Execute raw SQL only with bound parameters.

    Prefer ORM queries. This helper exists for rare administrative scripts.
    """
    return db.session.execute(text(sql), params)
