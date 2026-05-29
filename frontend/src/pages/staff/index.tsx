import { useEffect, useMemo, useState } from "react";
import { PageShell, StatCard, StatusBadge, Alert, ButtonLink, EmptyState } from "../../components/ui";
import { useRequireAuth } from "../../lib/useRequireAuth";
import { fetchSamples } from "../../lib/api";
import type { SampleRow } from "../../types/sample";

export default function StaffDashboard() {
  const [samples, setSamples] = useState<SampleRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState("all");

  useRequireAuth();

  useEffect(() => {
    fetchSamples()
      .then(setSamples)
      .catch((err) => setError(err.message));
  }, []);

  const visibleSamples = useMemo(() => {
    return status === "all" ? samples : samples.filter((sample) => sample.status === status);
  }, [samples, status]);

  return (
    <PageShell wide>
      <section className="page-title">
        <div>
          <p className="eyebrow">Staff workspace</p>
          <h1>Field sample operations</h1>
          <p>View your submitted records, their review state, and next actions for ongoing sample workflows.</p>
        </div>
        <ButtonLink href="/operations" tone="secondary">All operations</ButtonLink>
      </section>

      {error && <Alert tone="error">{error}</Alert>}

      <section className="kpi-strip">
        <StatCard label="Total samples" value={String(samples.length)} note="Staff-accessible records" />
        <StatCard label="Submitted" value={String(samples.filter((sample) => sample.status === "Submitted").length)} note="Awaiting reviewer action" />
        <StatCard label="Approved" value={String(samples.filter((sample) => sample.status === "Approved").length)} note="Ready for publication" />
        <StatCard label="Pending" value={String(samples.filter((sample) => sample.status === "Correction Requested" || sample.status === "Draft").length)} note="Needs updates or approval" />
      </section>

      <section className="section filter-bar">
        <label>
          <span className="muted">Filter status</span>
          <select value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="all">All statuses</option>
            <option value="Draft">Draft</option>
            <option value="Submitted">Submitted</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
            <option value="Correction Requested">Correction Requested</option>
          </select>
        </label>
      </section>

      <section className="section card">
        {visibleSamples.length === 0 ? (
          <EmptyState title="No samples found" message="Create sample records or choose a different status filter." />
        ) : (
          <div className="staff-table">
            <div className="table-row table-head">
              <div>Sample</div>
              <div>Status</div>
              <div>Verification</div>
              <div>Collection date</div>
              <div>Public</div>
            </div>
            {visibleSamples.map((sample) => (
              <div className="table-row" key={sample.id}>
                <div>{sample.sample_code}</div>
                <div><StatusBadge status={sample.status} /></div>
                <div><StatusBadge status={sample.verification_status} /></div>
                <div>{new Date(sample.collection_date).toLocaleDateString()}</div>
                <div><StatusBadge status={sample.public_visibility} /></div>
              </div>
            ))}
          </div>
        )}
      </section>
    </PageShell>
  );
}
