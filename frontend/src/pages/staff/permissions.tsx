import { useEffect, useState } from "react";
import { StaffLayout, Alert, EmptyState } from "../../components/ui";
import { useRequireAuth } from "../../lib/useRequireAuth";
import { fetchMyPermissions } from "../../lib/api";

export default function StaffPermissions() {
  const [data, setData] = useState<{
    role: { name: string | null; description: string | null };
    role_permissions: { key: string; description: string | null }[];
    user_overrides: { granted: boolean }[];
    effective_permissions: string[];
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useRequireAuth();

  useEffect(() => {
    fetchMyPermissions()
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <StaffLayout active="permissions">
      <section className="page-title">
        <p className="eyebrow">Access control</p>
        <h1>My permissions</h1>
        <p>View the permissions and access level granted to your account.</p>
      </section>

      {error && <Alert tone="error">{error}</Alert>}

      {!data && !error && <EmptyState title="Loading permissions" message="Retrieving your access information." />}

      {data && (
        <>
          <section className="section card">
            <h2>Role</h2>
            <div className="form-grid" style={{ marginTop: 12 }}>
              <div className="field">
                <label>Role name</label>
                <div className="readonly-field" style={{ fontWeight: 600, fontSize: "1.1rem" }}>{data.role.name || "—"}</div>
              </div>
              <div className="field">
                <label>Description</label>
                <div className="readonly-field">{data.role.description || "—"}</div>
              </div>
            </div>
          </section>

          <section className="section card">
            <h2>Granted permissions</h2>
            <p className="muted" style={{ marginBottom: 16 }}>
              Your role grants {data.role_permissions.length} permission{data.role_permissions.length !== 1 ? "s" : ""}.
            </p>
            {data.role_permissions.length === 0 ? (
              <p className="muted">No permissions assigned to this role.</p>
            ) : (
              <div className="permission-grid">
                {data.role_permissions.map((perm) => (
                  <div className="permission-chip" key={perm.key}>
                    <span className="permission-key">{perm.key}</span>
                    {perm.description && <span className="muted" style={{ fontSize: "0.8rem" }}>{perm.description}</span>}
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </StaffLayout>
  );
}