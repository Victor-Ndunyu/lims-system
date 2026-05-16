import { useEffect, useState } from "react";
import { AdminLayout, Alert, ButtonLink } from "../../components/ui";
import { fetchAdminUsers, AdminUser } from "../../lib/api";
import { useRequireRole } from "../../lib/useRequireAuth";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useRequireRole("admin");

  useEffect(() => {
    fetchAdminUsers()
      .then(setUsers)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <AdminLayout active="users">
      <section className="page-title">
        <div>
          <p className="eyebrow">User management</p>
          <h1>Staff accounts and access roles</h1>
          <p>Review registered users, active status, and assigned roles for platform operations.</p>
        </div>
        <ButtonLink href="/admin/users/new">Invite user</ButtonLink>
      </section>

      {error && <Alert tone="error">{error}</Alert>}

      <section className="section card">
        {users ? (
          <div className="admin-table">
            <div className="table-row table-head">
              <div>Name</div>
              <div>Email</div>
              <div>Role</div>
              <div>Status</div>
            </div>
            {users.map((user) => (
              <div className="table-row" key={user.id}>
                <div>{user.full_name}</div>
                <div>{user.email}</div>
                <div>{user.role_name || "Staff"}</div>
                <div>{user.is_active ? "Active" : "Inactive"}</div>
              </div>
            ))}
          </div>
        ) : (
          <p className="muted">Loading user roster…</p>
        )}
      </section>
    </AdminLayout>
  );
}
