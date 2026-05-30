"""Add recovery_codes table

Revision ID: a1b2c3d4e5f6
Revises: 1d7008dfde88
Create Date: 2026-05-16 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "1d7008dfde88"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "recovery_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("code_hash", sa.String(length=255), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("recovery_codes", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_recovery_codes_user_id"), ["user_id"], unique=False)


def downgrade():
    with op.batch_alter_table("recovery_codes", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_recovery_codes_user_id"))

    op.drop_table("recovery_codes")
