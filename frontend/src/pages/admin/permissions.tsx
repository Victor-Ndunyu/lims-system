import { useEffect, useMemo, useState, type FormEvent } from "react";
import { AdminLayout, Alert, ButtonLink, Button, StatusBadge } from "../../components/ui";
import { assignPermissionsToRole, fetchAdminPermissions, fetchAdminRoles, type PermissionRead, type RoleRead } from "../../lib/api";
import { useRequireRole } from "../../lib/useRequireAuth";

export default function PermissionManagementPage() {
  const [roles, setRoles] = useState<RoleRead[]>([]);
  const [permissions, setPermissions] = useState<PermissionRead[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<string>("");
  const [selectedPermissions, setSelectedPermissions] = useState<Set<string>>(new Set());
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useRequireRole("admin");

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchAdminRoles(), fetchAdminPermissions()])
      .then(([rolesData, permsData]) => {
        setRoles(rolesData);
        setPermissions(permsData);
        if (rolesData.length > 0) {
          setSelectedRoleId(rolesData[0].id);
          setSelectedPermissions(new Set(rolesData[0].permissions?.map((perm) => perm.permission_key) || []));
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const role = roles.find((item) => item.id === selectedRoleId);
    setSelectedPermissions(new Set(role?.permissions?.map((perm) => perm.permission_key) || []));
  }, [roles, selectedRoleId]);

  const selectedRole = useMemo(() => roles.find((role) => role.id === selectedRoleId), [roles, selectedRoleId]);

  function togglePermission(permissionKey: string) {
    setSelectedPermissions((current) => {
      const next = new Set(current);
      if (next.has(permissionKey)) {
        next.delete(permissionKey);
      } else {
        next.add(permissionKey);
      }
      return next;
    });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedRoleId) {
      setError("Select a role first.");
      return;
    }
    setSaving(true);
    setError(null);
    setStatusMessage(null);

    try {
      await assignPermissionsToRole(selectedRoleId, Array.from(selectedPermissions));
      setStatusMessage("Permissions saved successfully.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save permissions");
    } finally {
      setSaving(false);
    }
  }

  return (
    <AdminLayout active="permissions">
      <section className="page-title">
        <div>
          <p className="eyebrow">Permission controls</p>
          <h1>Role permission management</h1>
          <p>Assign and tune permissions for roles so admin workflows can remain secure and auditable.</p>
        </div>
        <ButtonLink href="/admin/users" tone="secondary">
          User management
        </ButtonLink>
      </section>

      {error && <Alert tone="error">{error}</Alert>}
      {statusMessage && <Alert tone="success">{statusMessage}</Alert>}

      <section className="section card">
        <form onSubmit={handleSubmit} className="form-grid">
          <label className="form-field">
            <span>Role</span>
            <select value={selectedRoleId} onChange={(event) => setSelectedRoleId(event.target.value)}>
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.role_name.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </label>

          <div className="form-field">
            <span>Role description</span>
            <p className="muted">{selectedRole?.description || "No description available."}</p>
          </div>

          <div className="form-field permission-grid">
            <span>Permissions</span>
            {loading ? (
              <p className="muted">Loading permissions…</p>
            ) : (
              <div className="permission-list">
                {permissions.map((permission) => (
                  <label key={permission.id} className="permission-item">
                    <input
                      type="checkbox"
                      checked={selectedPermissions.has(permission.permission_key)}
                      onChange={() => togglePermission(permission.permission_key)}
                    />
                    <div>
                      <strong>{permission.permission_key}</strong>
                      <p className="muted">{permission.description}</p>
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>

          <div className="form-actions">
            <Button type="submit" tone="primary">{saving ? "Saving permissions…" : "Save permissions"}</Button>
          </div>
        </form>
      </section>

      <section className="section grid grid-2">
        <article className="card micro-grid">
          <p className="eyebrow">Permission preview</p>
          <h3>Currently assigned permissions</h3>
          {selectedRole?.permissions?.length ? (
            selectedRole.permissions.map((permission) => (
              <StatusBadge key={permission.id} status={permission.permission_key} />
            ))
          ) : (
            <p className="muted">This role currently has no assigned permissions.</p>
          )}
        </article>
        <article className="card micro-grid">
          <p className="eyebrow">Security note</p>
          <h3>Admin-only role management</h3>
          <p className="muted">Changes here affect backend authorization for all staff and admin actions.</p>
        </article>
      </section>
    </AdminLayout>
  );
}
