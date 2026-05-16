"""Initial schema for field sample management system.

Revision ID: 0001_initial
Revises: 
Create Date: 2026-05-11 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("role_name", sa.String(length=64), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_roles_role_name"), "roles", ["role_name"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=50), nullable=True, unique=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_phone_number"), "users", ["phone_number"], unique=True)
    op.create_index(op.f("ix_users_role_id"), "users", ["role_id"])

    op.create_table(
        "sample_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_sample_types_name"), "sample_types", ["name"], unique=True)

    op.create_table(
        "locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("country", sa.String(length=128), nullable=False),
        sa.Column("county", sa.String(length=128), nullable=True),
        sa.Column("subcounty", sa.String(length=128), nullable=True),
        sa.Column("site_name", sa.String(length=255), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("altitude", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_locations_country"), "locations", ["country"])
    op.create_index(op.f("ix_locations_county"), "locations", ["county"])
    op.create_index(op.f("ix_locations_subcounty"), "locations", ["subcounty"])
    op.create_index(op.f("ix_locations_site_name"), "locations", ["site_name"])

    op.create_table(
        "samples",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("sample_code", sa.String(length=128), nullable=False, unique=True),
        sa.Column("sample_type_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sample_types.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("collection_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("collector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(length=60), nullable=False, server_default="Draft"),
        sa.Column("verification_status", sa.String(length=60), nullable=False, server_default="Pending"),
        sa.Column("public_visibility", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_samples_sample_code"), "samples", ["sample_code"], unique=True)
    op.create_index(op.f("ix_samples_sample_type_id"), "samples", ["sample_type_id"])
    op.create_index(op.f("ix_samples_collection_date"), "samples", ["collection_date"])
    op.create_index(op.f("ix_samples_collector_id"), "samples", ["collector_id"])
    op.create_index(op.f("ix_samples_location_id"), "samples", ["location_id"])
    op.create_index(op.f("ix_samples_status"), "samples", ["status"])
    op.create_index(op.f("ix_samples_verification_status"), "samples", ["verification_status"])
    op.create_index(op.f("ix_samples_public_visibility"), "samples", ["public_visibility"])

    op.create_table(
        "attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("sample_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("samples.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=100), nullable=False),
        sa.Column("file_url", sa.String(length=1024), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_attachments_sample_id"), "attachments", ["sample_id"])
    op.create_index(op.f("ix_attachments_uploaded_by"), "attachments", ["uploaded_by"])

    op.create_table(
        "sample_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("sample_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("samples.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("decision", sa.String(length=64), nullable=False),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_sample_reviews_sample_id"), "sample_reviews", ["sample_id"])
    op.create_index(op.f("ix_sample_reviews_reviewer_id"), "sample_reviews", ["reviewer_id"])
    op.create_index(op.f("ix_sample_reviews_decision"), "sample_reviews", ["decision"])

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("table_name", sa.String(length=128), nullable=False),
        sa.Column("record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("old_values", postgresql.JSONB(), nullable=True),
        sa.Column("new_values", postgresql.JSONB(), nullable=True),
        sa.Column("performed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("performed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
    )
    op.create_index(op.f("ix_audit_logs_table_name"), "audit_logs", ["table_name"])
    op.create_index(op.f("ix_audit_logs_record_id"), "audit_logs", ["record_id"])
    op.create_index(op.f("ix_audit_logs_performed_by"), "audit_logs", ["performed_by"])

    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("device_info", sa.String(length=512), nullable=True),
    )
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"])
    op.create_index(op.f("ix_sessions_token_hash"), "sessions", ["token_hash"], unique=True)
    op.create_index(op.f("ix_sessions_expires_at"), "sessions", ["expires_at"])


def downgrade():
    op.drop_index(op.f("ix_sessions_expires_at"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_token_hash"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_table("sessions")

    op.drop_index(op.f("ix_audit_logs_performed_by"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_record_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_table_name"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_sample_reviews_decision"), table_name="sample_reviews")
    op.drop_index(op.f("ix_sample_reviews_reviewer_id"), table_name="sample_reviews")
    op.drop_index(op.f("ix_sample_reviews_sample_id"), table_name="sample_reviews")
    op.drop_table("sample_reviews")

    op.drop_index(op.f("ix_attachments_uploaded_by"), table_name="attachments")
    op.drop_index(op.f("ix_attachments_sample_id"), table_name="attachments")
    op.drop_table("attachments")

    op.drop_index(op.f("ix_samples_public_visibility"), table_name="samples")
    op.drop_index(op.f("ix_samples_verification_status"), table_name="samples")
    op.drop_index(op.f("ix_samples_status"), table_name="samples")
    op.drop_index(op.f("ix_samples_location_id"), table_name="samples")
    op.drop_index(op.f("ix_samples_collector_id"), table_name="samples")
    op.drop_index(op.f("ix_samples_collection_date"), table_name="samples")
    op.drop_index(op.f("ix_samples_sample_type_id"), table_name="samples")
    op.drop_index(op.f("ix_samples_sample_code"), table_name="samples")
    op.drop_table("samples")

    op.drop_index(op.f("ix_locations_site_name"), table_name="locations")
    op.drop_index(op.f("ix_locations_subcounty"), table_name="locations")
    op.drop_index(op.f("ix_locations_county"), table_name="locations")
    op.drop_index(op.f("ix_locations_country"), table_name="locations")
    op.drop_table("locations")

    op.drop_index(op.f("ix_sample_types_name"), table_name="sample_types")
    op.drop_table("sample_types")

    op.drop_index(op.f("ix_users_role_id"), table_name="users")
    op.drop_index(op.f("ix_users_phone_number"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_roles_role_name"), table_name="roles")
    op.drop_table("roles")
