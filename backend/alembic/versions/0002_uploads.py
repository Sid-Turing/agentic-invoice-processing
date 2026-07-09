"""uploads table — transient blob channel for remote extraction

Revision ID: 0002_uploads
Revises: 0001_initial
Create Date: 2026-07-09
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_uploads"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "uploads",
        sa.Column("attachment_id", sa.String(), primary_key=True),
        sa.Column("conversation_id", sa.String()),
        sa.Column("mime", sa.String()),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_uploads_conversation_id", "uploads", ["conversation_id"])


def downgrade() -> None:
    op.drop_index("ix_uploads_conversation_id", table_name="uploads")
    op.drop_table("uploads")
