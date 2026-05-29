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

type NavItem = {
  href: string;
  label: string;
  permission?: string;
};

const NAV_ITEMS: NavItem[] = [
  { href: "/staff", label: "Sample records", permission: "create_sample_record" },
  { href: "/admin/samples/new", label: "New sample", permission: "create_sample_record" },
  { href: "/admin", label: "Dashboard", permission: "view_dashboards" },
  { href: "/admin/users", label: "User management", permission: "manage_users" },
  { href: "/admin/permissions", label: "Role permissions", permission: "manage_users" },
  { href: "/staff/permissions", label: "My permissions" },
  { href: "/staff/settings", label: "Settings" },
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

  const visibleNav = NAV_ITEMS.filter((item) => {
    if (!item.permission) return true;
    return effective.has(item.permission);
  });

  return (
    <PageShell wide>
      <div className="admin-layout">
        <aside className="sidebar">
          <p className="eyebrow">Navigation</p>
          <h2 style={{ margin: "0 0 16px" }}>Operations</h2>
          {visibleNav.map((item) => (
            <Link key={item.href} href={item.href}>
              <span aria-hidden="true" className="nav-dot" />
              {item.label}
            </Link>
          ))}
          <div className="sidebar-section">
            <p style={{ color: "rgba(255,255,255,0.72)", margin: 0 }}>
              {user?.full_name || "User"} &middot; {perms?.role.name || "Loading role..."}
            </p>
          </div>
        </aside>
        <section>
          {error && <Alert tone="error">{error}</Alert>}
          <section className="page-title">
            <div>
              <p className="eyebrow">Welcome{user ? `, ${user.full_name}` : ""}</p>
              <h1>Operations hub</h1>
              <p>
                {perms
                  ? `You are signed in as "${perms.role.name || "User"}". Use the sidebar to navigate to your available tools.`
                  : "Loading your access permissions..."}
              </p>
            </div>
          </section>
          <section className="section">
            <div className="card" style={{ padding: "var(--space-5)" }}>
              <h3>Your role</h3>
              <div className="form-grid" style={{ marginTop: 12 }}>
                <div className="field">
                  <label>Role</label>
                  <div className="readonly-field" style={{ fontWeight: 600, fontSize: "1.1rem" }}>{perms?.role.name || "—"}</div>
                </div>
                <div className="field">
                  <label>Description</label>
                  <div className="readonly-field">{perms?.role.description || "—"}</div>
                </div>
                <div className="field">
                  <label>Granted permissions</label>
                  <div className="readonly-field">{perms?.effective_permissions.length ?? 0} permission{(perms?.effective_permissions.length ?? 0) !== 1 ? "s" : ""}</div>
                </div>
              </div>
            </div>
          </section>
        </section>
      </div>
    </PageShell>
  );
}