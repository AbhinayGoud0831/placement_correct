"""add sample jobs table

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sample_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("level", sa.String(50), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("extracted_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_sample_jobs_title", "sample_jobs", ["title"])


def downgrade():
    op.drop_index("ix_sample_jobs_title", table_name="sample_jobs")
    op.drop_table("sample_jobs")
