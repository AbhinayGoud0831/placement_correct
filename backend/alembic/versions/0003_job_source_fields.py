"""add external job source metadata

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-09
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("sample_jobs", sa.Column("external_id", sa.String(500), nullable=True))
    op.add_column("sample_jobs", sa.Column("source", sa.String(100), nullable=False, server_default="demo"))
    op.add_column("sample_jobs", sa.Column("url", sa.String(2000), nullable=True))
    op.add_column("sample_jobs", sa.Column("location", sa.String(255), nullable=True))
    op.add_column("sample_jobs", sa.Column("employment_type", sa.String(80), nullable=True))
    op.add_column("sample_jobs", sa.Column("remote", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_unique_constraint("uq_sample_jobs_external_id", "sample_jobs", ["external_id"])
    op.create_index("ix_sample_jobs_external_id", "sample_jobs", ["external_id"])


def downgrade():
    op.drop_index("ix_sample_jobs_external_id", table_name="sample_jobs")
    op.drop_constraint("uq_sample_jobs_external_id", "sample_jobs", type_="unique")
    op.drop_column("sample_jobs", "remote")
    op.drop_column("sample_jobs", "employment_type")
    op.drop_column("sample_jobs", "location")
    op.drop_column("sample_jobs", "url")
    op.drop_column("sample_jobs", "source")
    op.drop_column("sample_jobs", "external_id")
