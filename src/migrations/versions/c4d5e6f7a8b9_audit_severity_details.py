"""audit log severity and details

Revision ID: c4d5e6f7a8b9
Revises: b2c3d4e5f6a7
Create Date: 2026-05-16

"""
from alembic import op
import sqlalchemy as sa


revision = "c4d5e6f7a8b9"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("audit_logs", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("severity", sa.String(length=20), server_default="INFO", nullable=False)
        )
        batch_op.add_column(sa.Column("details", sa.Text(), nullable=True))
        batch_op.create_index(batch_op.f("ix_audit_logs_severity"), ["severity"], unique=False)
        batch_op.alter_column("target_type", existing_type=sa.String(length=50), nullable=True)


def downgrade():
    with op.batch_alter_table("audit_logs", schema=None) as batch_op:
        batch_op.alter_column("target_type", existing_type=sa.String(length=50), nullable=False)
        batch_op.drop_index(batch_op.f("ix_audit_logs_severity"))
        batch_op.drop_column("details")
        batch_op.drop_column("severity")
