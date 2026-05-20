"""Add Supabase row level security policies.

Revision ID: 0004_supabase_rls
Revises: 0003_rbac_permissions
Create Date: 2026-05-20 00:00:00.000000
"""

from alembic import op


revision = "0004_supabase_rls"
down_revision = "0003_rbac_permissions"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        create or replace function public.app_current_user_id()
        returns uuid
        language sql
        stable
        security definer
        set search_path = public
        as $$
            select u.id
            from public.users u
            where lower(u.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
              and u.is_active is true
            limit 1
        $$;

        create or replace function public.app_current_user_is_admin()
        returns boolean
        language sql
        stable
        security definer
        set search_path = public
        as $$
            select exists (
                select 1
                from public.users u
                join public.roles r on r.id = u.role_id
                where u.id = public.app_current_user_id()
                  and r.role_name in ('super_admin', 'admin')
            )
        $$;

        create or replace function public.app_current_user_has_permission(permission_key_input text)
        returns boolean
        language sql
        stable
        security definer
        set search_path = public
        as $$
            with current_user_row as (
                select u.id, u.role_id
                from public.users u
                where u.id = public.app_current_user_id()
            ),
            target_permission as (
                select p.id
                from public.permissions p
                where p.permission_key = permission_key_input
            )
            select case
                when public.app_current_user_is_admin() then true
                when exists (
                    select 1
                    from current_user_row cu
                    join public.user_permissions up on up.user_id = cu.id
                    join target_permission tp on tp.id = up.permission_id
                    where up.granted is false
                ) then false
                when exists (
                    select 1
                    from current_user_row cu
                    join public.user_permissions up on up.user_id = cu.id
                    join target_permission tp on tp.id = up.permission_id
                    where up.granted is true
                ) then true
                when exists (
                    select 1
                    from current_user_row cu
                    join public.role_permissions rp on rp.role_id = cu.role_id
                    join target_permission tp on tp.id = rp.permission_id
                ) then true
                else false
            end
        $$;

        create or replace function public.app_can_read_sample(sample_row public.samples)
        returns boolean
        language sql
        stable
        security definer
        set search_path = public
        as $$
            select
                (sample_row.public_visibility is true and sample_row.status = 'Approved')
                or public.app_current_user_is_admin()
                or sample_row.collector_id = public.app_current_user_id()
                or public.app_current_user_has_permission('edit_all_records')
                or public.app_current_user_has_permission('approve_records')
                or public.app_current_user_has_permission('publish_records')
                or public.app_current_user_has_permission('export_data')
        $$;

        create or replace function public.app_can_update_sample(sample_row public.samples)
        returns boolean
        language sql
        stable
        security definer
        set search_path = public
        as $$
            select
                public.app_current_user_is_admin()
                or public.app_current_user_has_permission('edit_all_records')
                or (
                    sample_row.collector_id = public.app_current_user_id()
                    and public.app_current_user_has_permission('edit_own_record')
                    and sample_row.status in ('Draft', 'Submitted', 'Correction Requested')
                )
        $$;
        """
    )

    for table in [
        "roles",
        "users",
        "permissions",
        "role_permissions",
        "user_permissions",
        "sample_types",
        "locations",
        "samples",
        "attachments",
        "sample_reviews",
        "sample_versions",
        "audit_logs",
        "sessions",
    ]:
        op.execute(f"alter table public.{table} enable row level security")

    op.execute(
        """
        create policy "admins manage roles"
        on public.roles
        for all
        to authenticated
        using (public.app_current_user_is_admin())
        with check (public.app_current_user_is_admin());

        create policy "admins manage permissions"
        on public.permissions
        for all
        to authenticated
        using (public.app_current_user_is_admin())
        with check (public.app_current_user_is_admin());

        create policy "admins manage role permissions"
        on public.role_permissions
        for all
        to authenticated
        using (public.app_current_user_is_admin())
        with check (public.app_current_user_is_admin());

        create policy "admins manage user permissions"
        on public.user_permissions
        for all
        to authenticated
        using (public.app_current_user_is_admin())
        with check (public.app_current_user_is_admin());

        create policy "users read own profile admins read all"
        on public.users
        for select
        to authenticated
        using (public.app_current_user_is_admin() or id = public.app_current_user_id());

        create policy "admins insert users"
        on public.users
        for insert
        to authenticated
        with check (public.app_current_user_is_admin());

        create policy "admins update users"
        on public.users
        for update
        to authenticated
        using (public.app_current_user_is_admin())
        with check (public.app_current_user_is_admin());

        create policy "admins delete users"
        on public.users
        for delete
        to authenticated
        using (public.app_current_user_is_admin());

        create policy "authenticated read sample types"
        on public.sample_types
        for select
        to authenticated
        using (true);

        create policy "admins manage sample types"
        on public.sample_types
        for all
        to authenticated
        using (public.app_current_user_is_admin())
        with check (public.app_current_user_is_admin());

        create policy "authenticated read locations"
        on public.locations
        for select
        to authenticated
        using (true);

        create policy "admins manage locations"
        on public.locations
        for all
        to authenticated
        using (public.app_current_user_is_admin())
        with check (public.app_current_user_is_admin());

        create policy "public reads published samples"
        on public.samples
        for select
        to anon, authenticated
        using (public.app_can_read_sample(samples));

        create policy "permitted users insert samples"
        on public.samples
        for insert
        to authenticated
        with check (
            public.app_current_user_is_admin()
            or public.app_current_user_has_permission('edit_all_records')
            or (
                public.app_current_user_has_permission('create_sample_record')
                and collector_id = public.app_current_user_id()
            )
        );

        create policy "permitted users update samples"
        on public.samples
        for update
        to authenticated
        using (public.app_can_update_sample(samples))
        with check (public.app_can_update_sample(samples));

        create policy "admins delete samples"
        on public.samples
        for delete
        to authenticated
        using (public.app_current_user_is_admin());

        create policy "public reads published attachments"
        on public.attachments
        for select
        to anon, authenticated
        using (
            exists (
                select 1
                from public.samples s
                where s.id = attachments.sample_id
                  and public.app_can_read_sample(s)
            )
        );

        create policy "permitted users insert attachments"
        on public.attachments
        for insert
        to authenticated
        with check (
            public.app_current_user_has_permission('upload_attachments')
            and exists (
                select 1
                from public.samples s
                where s.id = attachments.sample_id
                  and public.app_can_update_sample(s)
            )
        );

        create policy "permitted users update attachments"
        on public.attachments
        for update
        to authenticated
        using (
            public.app_current_user_has_permission('upload_attachments')
            and exists (
                select 1
                from public.samples s
                where s.id = attachments.sample_id
                  and public.app_can_update_sample(s)
            )
        )
        with check (
            public.app_current_user_has_permission('upload_attachments')
            and exists (
                select 1
                from public.samples s
                where s.id = attachments.sample_id
                  and public.app_can_update_sample(s)
            )
        );

        create policy "admins delete attachments"
        on public.attachments
        for delete
        to authenticated
        using (public.app_current_user_is_admin());

        create policy "reviewers read sample reviews"
        on public.sample_reviews
        for select
        to authenticated
        using (public.app_current_user_is_admin() or public.app_current_user_has_permission('approve_records'));

        create policy "reviewers insert sample reviews"
        on public.sample_reviews
        for insert
        to authenticated
        with check (public.app_current_user_is_admin() or public.app_current_user_has_permission('approve_records'));

        create policy "reviewers update sample reviews"
        on public.sample_reviews
        for update
        to authenticated
        using (public.app_current_user_is_admin() or public.app_current_user_has_permission('approve_records'))
        with check (public.app_current_user_is_admin() or public.app_current_user_has_permission('approve_records'));

        create policy "admins delete sample reviews"
        on public.sample_reviews
        for delete
        to authenticated
        using (public.app_current_user_is_admin());

        create policy "permitted users read sample versions"
        on public.sample_versions
        for select
        to authenticated
        using (
            public.app_current_user_is_admin()
            or exists (
                select 1
                from public.samples s
                where s.id = sample_versions.sample_id
                  and public.app_can_read_sample(s)
            )
        );

        create policy "admins manage sample versions"
        on public.sample_versions
        for all
        to authenticated
        using (public.app_current_user_is_admin())
        with check (public.app_current_user_is_admin());

        create policy "admins read audit logs"
        on public.audit_logs
        for select
        to authenticated
        using (public.app_current_user_is_admin());

        create policy "admins insert audit logs"
        on public.audit_logs
        for insert
        to authenticated
        with check (public.app_current_user_is_admin());

        create policy "admins update audit logs"
        on public.audit_logs
        for update
        to authenticated
        using (public.app_current_user_is_admin())
        with check (public.app_current_user_is_admin());

        create policy "admins read sessions"
        on public.sessions
        for select
        to authenticated
        using (public.app_current_user_is_admin());

        create policy "admins manage sessions"
        on public.sessions
        for all
        to authenticated
        using (public.app_current_user_is_admin())
        with check (public.app_current_user_is_admin());
        """
    )


def downgrade():
    for table, policies in {
        "sessions": ["admins read sessions", "admins manage sessions"],
        "audit_logs": ["admins read audit logs", "admins insert audit logs", "admins update audit logs"],
        "sample_versions": ["permitted users read sample versions", "admins manage sample versions"],
        "sample_reviews": [
            "reviewers read sample reviews",
            "reviewers insert sample reviews",
            "reviewers update sample reviews",
            "admins delete sample reviews",
        ],
        "attachments": [
            "public reads published attachments",
            "permitted users insert attachments",
            "permitted users update attachments",
            "admins delete attachments",
        ],
        "samples": [
            "public reads published samples",
            "permitted users insert samples",
            "permitted users update samples",
            "admins delete samples",
        ],
        "locations": ["authenticated read locations", "admins manage locations"],
        "sample_types": ["authenticated read sample types", "admins manage sample types"],
        "users": [
            "users read own profile admins read all",
            "admins insert users",
            "admins update users",
            "admins delete users",
        ],
        "user_permissions": ["admins manage user permissions"],
        "role_permissions": ["admins manage role permissions"],
        "permissions": ["admins manage permissions"],
        "roles": ["admins manage roles"],
    }.items():
        for policy in policies:
            op.execute(f'drop policy if exists "{policy}" on public.{table}')

    for table in [
        "sessions",
        "audit_logs",
        "sample_versions",
        "sample_reviews",
        "attachments",
        "samples",
        "locations",
        "sample_types",
        "user_permissions",
        "role_permissions",
        "permissions",
        "users",
        "roles",
    ]:
        op.execute(f"alter table public.{table} disable row level security")

    op.execute(
        """
        drop function if exists public.app_can_update_sample(public.samples);
        drop function if exists public.app_can_read_sample(public.samples);
        drop function if exists public.app_current_user_has_permission(text);
        drop function if exists public.app_current_user_is_admin();
        drop function if exists public.app_current_user_id();
        """
    )
