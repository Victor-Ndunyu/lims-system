import { useEffect, useState } from "react";
import { AdminLayout, Alert, ButtonLink } from "../../components/ui";
import { fetchAdminUsers, fetchAdminRoles, deleteAdminUser, updateAdminUser, type AdminUser, type RoleRead } from "../../lib/api";
import { useRequireRole } from "../../lib/useRequireAuth";
import { getStoredUser } from "../../lib/session";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[] | null>(null);
  const [roles, setRoles] = useState<RoleRead[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useRequireRole("admin");

  useEffect(() => {
    Promise.all([fetchAdminUsers(), fetchAdminRoles()])
      .then(([usersData, rolesData]) => {
        setUsers(usersData);
        setRoles(rolesData);
      })
      .catch((err) => setError(err.message));
  }, []);

  const currentUser = getStoredUser();

  async function handleRoleChange(userId: string, roleName: string) {
    try {
      setError(null);
      setSuccess(null);
      await updateAdminUser(userId, { role_name: roleName });
      setUsers((prev) =>
        prev
          ? prev.map((u) => (u.id === userId ? { ...u, role_name: roleName } : u))
          : prev
      );
      setSuccess("User role updated");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update role");
    }
  }

  async function handleToggleActive(userId: string, currentActive: boolean) {
    try {
      setError(null);
      setSuccess(null);
      await updateAdminUser(userId, { is_active: !currentActive });
      setUsers((prev) =>
        prev
          ? prev.map((u) => (u.id === userId ? { ...u, is_active: !currentActive } : u))
          : prev
      );
      setSuccess(`User ${currentActive ? "deactivated" : "activated"}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update status");
    }
  }

  async function handleDelete(userId: string, userName: string) {
    if (!window.confirm(`Remove ${userName} from the platform? This cannot be undone.`)) return;
    try {
      setError(null);
      setSuccess(null);
      await deleteAdminUser(userId);
      setUsers((prev) => (prev ? prev.filter((u) => u.id !== userId) : prev));
      setSuccess(`${userName} removed`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete user");
    }
  }

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
      {success && <Alert tone="success">{success}</Alert>}

      <section className="section card">
        {users ? (
          <div className="admin-table">
            <div className="table-row table-head">
              <div>Name</div>
              <div>Email</div>
              <div>Role</div>
              <div>Status</div>
              <div>Actions</div>
            </div>
            {users.map((user) => (
              <div className="table-row" key={user.id}>
                <div className="cell-name">{user.full_name}</div>
                <div className="cell-email">{user.email}</div>
                <div className="cell-role">
                  <select
                    className="role-select"
                    value={user.role_name || ""}
                    onChange={(e) => handleRoleChange(user.id, e.target.value)}
                  >
                    <option value="" disabled>Select role</option>
                    {roles.map((r) => (
                      <option key={r.id} value={r.role_name}>{r.role_name}</option>
                    ))}
                  </select>
                </div>
                <div className="cell-status">
                  <button
                    type="button"
                    className={`badge ${user.is_active ? "status-approved" : "status-draft"}`}
                    onClick={() => handleToggleActive(user.id, user.is_active)}
                    title={user.is_active ? "Deactivate user" : "Activate user"}
                  >
                    {user.is_active ? "Active" : "Inactive"}
                  </button>
                </div>
                <div className="cell-actions">
                  {currentUser?.id !== user.id && (
                    <button
                      type="button"
                      className="button button-ghost button-delete"
                      onClick={() => handleDelete(user.id, user.full_name)}
                      title="Remove user"
                    >
                      Remove
                    </button>
                  )}
                </div>
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
