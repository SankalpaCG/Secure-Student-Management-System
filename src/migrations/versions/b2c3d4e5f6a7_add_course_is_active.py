"""add course is_active

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-16

"""
from alembic import op
import sqlalchemy as sa


revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("courses", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False)
        )


def downgrade():
    with op.batch_alter_table("courses", schema=None) as batch_op:
        batch_op.drop_column("is_active")
