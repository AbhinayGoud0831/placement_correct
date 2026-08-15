"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-09
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "students",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_students_email", "students", ["email"])

    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("extracted_data", sa.JSON(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "job_descriptions",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("extracted_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "analyses",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("resumes.id"), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("job_descriptions.id"), nullable=False),
        sa.Column("fit_score", sa.Float(), nullable=False),
        sa.Column("skills_score", sa.Float(), nullable=False),
        sa.Column("experience_score", sa.Float(), nullable=False),
        sa.Column("education_score", sa.Float(), nullable=False),
        sa.Column("matching_skills", sa.JSON(), nullable=True),
        sa.Column("missing_skills", sa.JSON(), nullable=True),
        sa.Column("recommendations", sa.JSON(), nullable=True),
        sa.Column("interview_prep", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table("analyses")
    op.drop_table("job_descriptions")
    op.drop_table("resumes")
    op.drop_index("ix_students_email", table_name="students")
    op.drop_table("students")
