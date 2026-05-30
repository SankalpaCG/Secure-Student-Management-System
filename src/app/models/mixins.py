from datetime import datetime

from app.extensions import db


class TimestampMixin:
    """Adds created_at and updated_at columns."""

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
