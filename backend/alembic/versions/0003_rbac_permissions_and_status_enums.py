"""Add RBAC permissions and PostgreSQL status enums.

Revision ID: 0003_rbac_permissions
Revises: 0002_add_sample_versions
Create Date: 2026-05-20 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0003_rbac_permissions"
down_revision = "0002_add_sample_versions"
branch_labels = None
depends_on = None


sample_status = postgresql.ENUM(
    "Draft",
    "Submitted",
    "Approved",
    "Rejected",
    "Correction Requested",
    "Archived",
    name="sample_status",
    create_type=False,
)
verification_status = postgresql.ENUM(
    "Draft",
    "Pending",
    "Approved",
    "Rejected",
    name="verification_status",
    create_type=False,
)
review_decision = postgresql.ENUM(
    "Approved",
    "Rejected",
    "Correction Requested",
    name="review_decision",
    create_type=False,
)


def upgrade():
    bind = op.get_bind()

    sample_status.create(bind, checkfirst=True)
    verification_status.create(bind, checkfirst=True)
    review_decision.create(bind, checkfirst=True)

    op.alter_column("samples", "status", server_default=None)
    op.alter_column("samples", "verification_status", server_default=None)
    op.alter_column(
        "samples",
        "status",
        existing_type=sa.String(length=60),
        type_=sample_status,
        existing_nullable=False,
        postgresql_using="status::sample_status",
        server_default=sa.text("'Draft'::sample_status"),
    )
    op.alter_column(
        "samples",
        "verification_status",
        existing_type=sa.String(length=60),
        type_=verification_status,
        existing_nullable=False,
        postgresql_using="verification_status::verification_status",
        server_default=sa.text("'Pending'::verification_status"),
    )
    op.alter_column(
        "sample_reviews",
        "decision",
        existing_type=sa.String(length=64),
        type_=review_decision,
        existing_nullable=False,
        postgresql_using="decision::review_decision",
    )

    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("permission_key", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_permissions_permission_key"), "permissions", ["permission_key"], unique=True)

    op.create_table(
        "role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(op.f("ix_role_permissions_role_id"), "role_permissions", ["role_id"])
    op.create_index(op.f("ix_role_permissions_permission_id"), "role_permissions", ["permission_id"])

    op.create_table(
        "user_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "permission_id", name="uq_user_permissions_user_id_permission_id"),
    )
    op.create_index(op.f("ix_user_permissions_user_id"), "user_permissions", ["user_id"])
    op.create_index(op.f("ix_user_permissions_permission_id"), "user_permissions", ["permission_id"])

    op.add_column("sessions", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))

    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"])
    op.create_index(op.f("ix_samples_created_at"), "samples", ["created_at"])
    op.create_index(op.f("ix_samples_updated_at"), "samples", ["updated_at"])


def downgrade():
    op.drop_index(op.f("ix_samples_updated_at"), table_name="samples")
    op.drop_index(op.f("ix_samples_created_at"), table_name="samples")
    op.drop_index(op.f("ix_audit_logs_action"), table_name="audit_logs")

    op.drop_column("sessions", "updated_at")

    op.drop_index(op.f("ix_user_permissions_permission_id"), table_name="user_permissions")
    op.drop_index(op.f("ix_user_permissions_user_id"), table_name="user_permissions")
    op.drop_table("user_permissions")

    op.drop_index(op.f("ix_role_permissions_permission_id"), table_name="role_permissions")
    op.drop_index(op.f("ix_role_permissions_role_id"), table_name="role_permissions")
    op.drop_table("role_permissions")

    op.drop_index(op.f("ix_permissions_permission_key"), table_name="permissions")
    op.drop_table("permissions")

    op.alter_column(
        "sample_reviews",
        "decision",
        existing_type=review_decision,
        type_=sa.String(length=64),
        existing_nullable=False,
        postgresql_using="decision::text",
    )
    op.alter_column(
        "samples",
        "verification_status",
        existing_type=verification_status,
        type_=sa.String(length=60),
        existing_nullable=False,
        postgresql_using="verification_status::text",
        server_default="Pending",
    )
    op.alter_column(
        "samples",
        "status",
        existing_type=sample_status,
        type_=sa.String(length=60),
        existing_nullable=False,
        postgresql_using="status::text",
        server_default="Draft",
    )

    review_decision.drop(op.get_bind(), checkfirst=True)
    verification_status.drop(op.get_bind(), checkfirst=True)
    sample_status.drop(op.get_bind(), checkfirst=True)
