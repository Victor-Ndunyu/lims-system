import { useEffect, useState } from "react";
import { AdminLayout, ButtonLink, StatCard, StatusBadge, Alert } from "../../components/ui";
import { fetchAdminCharts, fetchAdminStats, type AdminCharts, type AdminStats } from "../../lib/api";
import { getStoredUser } from "../../lib/session";
import { useRequireRole } from "../../lib/useRequireAuth";

export default function AdminHome() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [charts, setCharts] = useState<AdminCharts | null>(null);
  const [error, setError] = useState<string | null>(null);

  useRequireRole("admin");

  useEffect(() => {
    Promise.all([fetchAdminStats(), fetchAdminCharts()])
      .then(([statsData, chartsData]) => {
        setStats(statsData);
        setCharts(chartsData);
      })
      .catch((err) => setError(err.message));
  }, []);

  const user = getStoredUser();
  const welcomeName = user?.full_name || "Admin";

  return (
    <AdminLayout active="dashboard">
      <section className="page-title">
        <div>
          <p className="eyebrow">Admin portal</p>
          <h1>Welcome back, {welcomeName}</h1>
          <p>Track collection activity, approval trends, and user operations from the admin command center.</p>
        </div>
        <ButtonLink href="/admin/samples/new">New sample</ButtonLink>
      </section>

      {error && <Alert tone="error">{error}</Alert>}

      <section className="kpi-strip">
        <StatCard label="Total users" value={stats ? String(stats.total_users) : "—"} note="Active staff and viewers" />
        <StatCard label="Active accounts" value={stats ? String(stats.active_users) : "—"} note="Enabled users" />
        <StatCard label="Submitted today" value={stats ? String(stats.records_submitted_today) : "—"} note="Field submissions" />
        <StatCard label="Pending approvals" value={stats ? String(stats.pending_approvals) : "—"} note="Reviewer queue" />
      </section>

      <section className="section grid grid-2">
        <article className="card">
          <div className="section-header">
            <div>
              <p className="eyebrow">Approval pipeline</p>
              <h2>Record status summary</h2>
            </div>
            <StatusBadge status="Admin only" />
          </div>
          {charts ? (
            <div className="record-list">
              {charts.records_by_status.map((item) => (
                <div className="public-record-card" key={item.status}>
                  <div>
                    <h3>{item.status}</h3>
                    <p className="muted">Records in current status</p>
                  </div>
                  <strong>{item.count}</strong>
                </div>
              ))}
            </div>
          ) : (
            <p className="muted">Loading live status data…</p>
          )}
        </article>

        <article className="card">
          <div className="section-header">
            <div>
              <p className="eyebrow">Role distribution</p>
              <h2>Users by role</h2>
            </div>
          </div>
          {charts ? (
            <div className="mini-chart" aria-label="User roles chart">
              {charts.users_by_role.map((item) => (
                <span key={item.role} style={{ height: `${Math.max(24, Math.min(96, item.count * 12))}%` }} title={`${item.role}: ${item.count}`} />
              ))}
            </div>
          ) : (
            <p className="muted">Loading role analytics…</p>
          )}
          <p className="muted">Permission-aware user composition across the platform.</p>
        </article>
      </section>

      <section className="section grid grid-3">
        <article className="card">
          <p className="eyebrow">Operational insight</p>
          <h3>Sample type activity</h3>
          <div className="record-list">
            {charts?.records_by_type.map((item) => (
              <div className="public-record-card" key={item.sample_type_id}>
                <div>
                  <p>{item.sample_type_id}</p>
                  <p className="muted">Sample type count</p>
                </div>
                <strong>{item.count}</strong>
              </div>
            ))}
          </div>
        </article>
        <article className="card">
          <p className="eyebrow">User operations</p>
          <h3>Manage accounts</h3>
          <p className="muted">Create, assign roles, and tune access boundaries to reduce privilege drift.</p>
          <div style={{ marginTop: 18 }}>
            <ButtonLink href="/admin/users" tone="secondary">
              Open user management
            </ButtonLink>
          </div>
        </article>
        <article className="card micro-grid">
          <p className="eyebrow">Security note</p>
          <h3>Backend-enforced RBAC</h3>
          <p className="muted">All privileged actions are enforced on the server, not just in the UI.</p>
        </article>
      </section>
    </AdminLayout>
  );
}
