"""Add reports tables

Revision ID: 004
Revises: 003
Create Date: 2025-01-28 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id"),
            nullable=True,
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("subtitle", sa.String(), nullable=True),
        sa.Column("author", sa.String(), nullable=True),
        sa.Column("template_id", sa.String(), default="business_report_v1"),
        sa.Column("outline_json", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(), default="created"),
        sa.Column("progress_pct", sa.Integer(), default=0),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("pdf_path", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_reports_user_id", "reports", ["user_id"])

    op.create_table(
        "report_sections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "report_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("reports.id"),
            nullable=False,
        ),
        sa.Column("chapter_number", sa.String(), nullable=False),
        sa.Column("chapter_title", sa.String(), nullable=False),
        sa.Column("section_order", sa.Integer(), nullable=False),
        sa.Column("section_title", sa.String(), nullable=False),
        sa.Column("content_markdown", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), default="pending"),
        sa.Column("word_count", sa.Integer(), default=0),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_report_sections_report_id", "report_sections", ["report_id"])


def downgrade() -> None:
    op.drop_index("ix_report_sections_report_id", table_name="report_sections")
    op.drop_table("report_sections")
    op.drop_index("ix_reports_user_id", table_name="reports")
    op.drop_table("reports")
