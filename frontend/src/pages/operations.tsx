import { useEffect, useState } from "react";
import Link from "next/link";
import { PageShell, Alert } from "../components/ui";
import { useRequireAuth } from "../lib/useRequireAuth";
import { fetchMyPermissions, fetchCurrentUser } from "../lib/api";
import { getStoredUser, updateStoredUser } from "../lib/session";

type PermissionData = {
  role: { name: string | null; description: string | null };
  role_permissions: { key: string; description: string | null }[];
  effective_permissions: string[];
};

type OperationLink = {
  href: string;
  label: string;
  description: string;
  permission?: string;
  adminOnly?: boolean;
};

const ALL_OPERATIONS: OperationLink[] = [
  { href: "/staff", label: "Sample records", description: "View and manage sample records", permission: "create_sample_record" },
  { href: "/admin/samples/new", label: "New sample", description: "Create a new sample record", permission: "create_sample_record" },
  { href: "/admin", label: "Admin dashboard", description: "Operational dashboards and statistics", permission: "view_dashboards" },
  { href: "/admin/users", label: "User management", description: "Manage user accounts and roles", permission: "manage_users" },
  { href: "/admin/permissions", label: "Role permissions", description: "Assign permissions to roles", permission: "manage_users" },
  { href: "/staff/permissions", label: "My permissions", description: "View your granted permissions" },
  { href: "/staff/settings", label: "Settings", description: "Change your password and preferences" },
];

export default function OperationsPage() {
  const [user, setUser] = useState(getStoredUser());
  const [perms, setPerms] = useState<PermissionData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useRequireAuth();

  useEffect(() => {
    fetchCurrentUser()
      .then((res) => {
        if (res.user) {
          updateStoredUser(res.user);
          setUser(res.user);
        }
      })
      .catch(() => {});

    fetchMyPermissions()
      .then(setPerms)
      .catch((err) => setError(err.message));
  }, []);

  const effective = new Set(perms?.effective_permissions ?? []);

  const visibleOperations = ALL_OPERATIONS.filter((op) => {
    if (!op.permission) return true;
    if (op.adminOnly) return false;
    return effective.has(op.permission);
  });

  return (
    <PageShell wide>
      <section className="page-title">
        <div>
          <p className="eyebrow">Operations</p>
          <h1>Welcome{user ? `, ${user.full_name}` : ""}</h1>
          <p>
            {perms
              ? `You are logged in as "${perms.role.name || "User"}". Select an operation below.`
              : "Loading your access permissions..."}
          </p>
        </div>
      </section>

      {error && <Alert tone="error">{error}</Alert>}

      <section className="section">
        <div className="operations-grid">
          {visibleOperations.map((op) => (
            <Link key={op.href} href={op.href} className="operation-card">
              <h3>{op.label}</h3>
              <p className="muted">{op.description}</p>
            </Link>
          ))}
        </div>
      </section>
    </PageShell>
  );
}