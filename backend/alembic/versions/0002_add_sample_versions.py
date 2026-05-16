"""Add sample version history tracking.

Revision ID: 0002_add_sample_versions
Revises: 0001_initial
Create Date: 2026-05-11 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0002_add_sample_versions"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sample_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("sample_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("samples.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("change_type", sa.String(length=64), nullable=False),
        sa.Column("snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_sample_versions_sample_id"), "sample_versions", ["sample_id"])
    op.create_index(op.f("ix_sample_versions_version_number"), "sample_versions", ["version_number"])
    op.create_index(op.f("ix_sample_versions_change_type"), "sample_versions", ["change_type"])
    op.create_index(op.f("ix_sample_versions_changed_by"), "sample_versions", ["changed_by"])
    op.create_unique_constraint("uq_sample_versions_sample_id_version_number", "sample_versions", ["sample_id", "version_number"])


def downgrade():
    op.drop_constraint("uq_sample_versions_sample_id_version_number", "sample_versions", type_="unique")
    op.drop_index(op.f("ix_sample_versions_changed_by"), table_name="sample_versions")
    op.drop_index(op.f("ix_sample_versions_change_type"), table_name="sample_versions")
    op.drop_index(op.f("ix_sample_versions_version_number"), table_name="sample_versions")
    op.drop_index(op.f("ix_sample_versions_sample_id"), table_name="sample_versions")
    op.drop_table("sample_versions")
