import Link from "next/link";
import { useRouter } from "next/router";
import { useEffect, useState, type ReactNode } from "react";
import { fetchCurrentUser, fetchMyPermissions, logout as apiLogout } from "../lib/api";
import { clearAuth, getStoredUser, updateStoredUser, type UserSession } from "../lib/session";

type ButtonTone = "primary" | "secondary" | "ghost";

export function Topbar() {
  const router = useRouter();
  const [user, setUser] = useState<UserSession | null>(null);

  useEffect(() => {
    setUser(getStoredUser());
    fetchCurrentUser()
      .then((res) => {
        if (res.user) {
          updateStoredUser(res.user);
          setUser(res.user);
        }
      })
      .catch(() => {});
  }, []);

  async function handleLogout() {
    try {
      await apiLogout();
    } catch {
      // ignore errors during logout cleanup
    }
    clearAuth();
    router.replace("/login");
  }

  return (
    <header className="topbar">
      <Link href="/" className="brand-lockup" aria-label="Animal Health Field Intelligence home">
        <span className="brand-mark" aria-hidden="true" />
        <span>Animal Health Field Intelligence</span>
      </Link>
      <nav aria-label="Primary navigation">
        <Link className="nav-link" href="/public">
          Public portal
        </Link>
      </nav>
      <div className="topbar-actions">
        {user ? (
          <>
            <Link className="nav-link" href="/operations">Operations</Link>
            <span className="nav-user">{user.full_name}</span>
            <button type="button" className="button button-ghost" onClick={handleLogout}>
              Sign out
            </button>
          </>
        ) : (
          <Link className="button button-secondary" href="/login">
            Sign in
          </Link>
        )}
      </div>
    </header>
  );
}

export function PageShell({ children, wide = false }: { children: ReactNode; wide?: boolean }) {
  return (
    <div className="site-shell">
      <Topbar />
      <main className={`page ${wide ? "page-wide" : ""}`}>{children}</main>
    </div>
  );
}

export function ButtonLink({
  href,
  children,
  tone = "primary",
}: {
  href: string;
  children: ReactNode;
  tone?: ButtonTone;
}) {
  return (
    <Link className={`button button-${tone}`} href={href}>
      {children}
    </Link>
  );
}

export function Button({
  children,
  tone = "primary",
  type = "button",
  onClick,
  disabled,
}: {
  children: ReactNode;
  tone?: ButtonTone;
  type?: "button" | "submit";
  onClick?: () => void;
  disabled?: boolean;
}) {
  return (
    <button className={`button button-${tone}`} type={type} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}

export function StatCard({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <article className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {note && <p className="muted">{note}</p>}
    </article>
  );
}

export function StatusBadge({ status }: { status: string | boolean }) {
  const label = typeof status === "boolean" ? (status ? "Published" : "Private") : status || "Unknown";
  const className = label.toLowerCase().replace(/\s+/g, "-");
  return <span className={`badge status-${className}`}>{label}</span>;
}

export function Alert({ children, tone }: { children: ReactNode; tone: "error" | "success" }) {
  return <div className={`alert alert-${tone}`}>{children}</div>;
}

export function AdminLayout({ children, active = "dashboard" }: { children: ReactNode; active?: string }) {
  const navItems = [
    { href: "/admin", label: "Dashboard", key: "dashboard" },
    { href: "/admin/samples", label: "Records", key: "records" },
    { href: "/admin/users", label: "User management", key: "users" },
    { href: "/admin/permissions", label: "Permissions", key: "permissions" },
    { href: "/admin/samples/new", label: "New sample", key: "new" },
  ];

  return (
    <PageShell wide>
      <div className="admin-layout">
        <aside className="sidebar">
          <p className="eyebrow">Operations</p>
          <h2 style={{ margin: "0 0 16px" }}>Surveillance workspace</h2>
          {navItems.map((item) => (
            <Link key={item.key} className={active === item.key ? "active" : ""} href={item.href}>
              <span aria-hidden="true" className="nav-dot" />
              {item.label}
            </Link>
          ))}
          <div className="sidebar-section">
            <p style={{ color: "rgba(255,255,255,0.72)", margin: 0 }}>
              Secure review, field sample tracking, and publication controls for verified animal-health records.
            </p>
          </div>
        </aside>
        <section>{children}</section>
      </div>
    </PageShell>
  );
}

export function StaffLayout({ children, active = "records" }: { children: ReactNode; active?: string }) {
  const [perms, setPerms] = useState<{ effective_permissions: string[] } | null>(null);
  const [permsLoaded, setPermsLoaded] = useState(false);

  useEffect(() => {
    fetchMyPermissions()
      .then((data) => { setPerms(data); setPermsLoaded(true); })
      .catch(() => { setPermsLoaded(true); });
  }, []);

  const effective = new Set(perms?.effective_permissions ?? []);

  const navItems = [
    { href: "/staff", label: "Sample records", key: "records" },
    { href: "/admin/samples/new", label: "New sample", key: "new", permission: "create_sample_record" },
    { href: "/admin", label: "Dashboard", key: "dashboard", permission: "view_dashboards" },
    { href: "/staff/permissions", label: "My permissions", key: "permissions" },
    { href: "/staff/settings", label: "Settings", key: "settings" },
  ];

  const visibleNav = !permsLoaded
    ? navItems
    : navItems.filter((item) => {
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
            <Link key={item.key} className={active === item.key ? "active" : ""} href={item.href}>
              <span aria-hidden="true" className="nav-dot" />
              {item.label}
            </Link>
          ))}
          <div className="sidebar-section">
            <p style={{ color: "rgba(255,255,255,0.72)", margin: 0 }}>
              Field sample operations &amp; account tools
            </p>
          </div>
        </aside>
        <section>{children}</section>
      </div>
    </PageShell>
  );
}

export function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <div className="empty-state">
      <p className="eyebrow">No records</p>
      <h2>{title}</h2>
      <p className="muted">{message}</p>
    </div>
  );
}
