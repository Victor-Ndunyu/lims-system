import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import { AdminLayout, Alert, ButtonLink, EmptyState, StatCard, StatusBadge } from "../../../components/ui";
import { fetchSamples } from "../../../lib/api";
import { SampleRow } from "../../../types/sample";

export default function SampleManagement() {
  const [samples, setSamples] = useState<SampleRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("all");

  useEffect(() => {
    fetchSamples()
      .then((data) => setSamples(data))
      .catch((err) => setError(err.message));
  }, []);

  const filteredSamples = useMemo(() => {
    return samples.filter((sample) => {
      const matchesQuery = `${sample.sample_code} ${sample.status} ${sample.verification_status}`.toLowerCase().includes(query.toLowerCase());
      const matchesStatus = status === "all" || sample.status === status;
      return matchesQuery && matchesStatus;
    });
  }, [query, samples, status]);

  return (
    <AdminLayout active="records">
      <section className="page-title">
        <div>
          <p className="eyebrow">Record management</p>
          <h1>Sample registry</h1>
          <p>Review field submissions, publication state, and verification status across all records.</p>
        </div>
        <ButtonLink href="/admin/samples/new">Create sample</ButtonLink>
      </section>

      <section className="kpi-strip">
        <StatCard label="Total records" value={String(samples.length)} note="Visible to staff" />
        <StatCard label="Submitted" value={String(samples.filter((sample) => sample.status === "Submitted").length)} note="Awaiting review" />
        <StatCard label="Approved" value={String(samples.filter((sample) => sample.status === "Approved").length)} note="Scientifically cleared" />
        <StatCard label="Published" value={String(samples.filter((sample) => sample.public_visibility).length)} note="Public portal visible" />
      </section>

      <section className="section">
        <div className="filter-bar">
          <input
            className="search-input"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search sample code or status"
            aria-label="Search samples"
          />
          <select className="search-input" value={status} onChange={(event) => setStatus(event.target.value)} aria-label="Filter samples by status">
            <option value="all">All statuses</option>
            <option value="Draft">Draft</option>
            <option value="Submitted">Submitted</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
          </select>
          <Link className="button button-secondary" href="/admin">
            Dashboard
          </Link>
        </div>
      </section>

      {error && <Alert tone="error">{error}</Alert>}

      <section className="section table-card">
        {filteredSamples.length === 0 ? (
          <EmptyState title="No matching sample records" message="Create a sample or adjust the search and status filters." />
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Status</th>
                <th>Verification</th>
                <th>Collection date</th>
                <th>Public</th>
              </tr>
            </thead>
            <tbody>
              {filteredSamples.map((sample) => (
                <tr key={sample.id}>
                  <td>
                    <Link href={`/admin/samples/${sample.id}`}>
                      <strong>{sample.sample_code}</strong>
                    </Link>
                  </td>
                  <td>
                    <StatusBadge status={sample.status} />
                  </td>
                  <td>
                    <StatusBadge status={sample.verification_status} />
                  </td>
                  <td>{new Date(sample.collection_date).toLocaleDateString()}</td>
                  <td>
                    <StatusBadge status={sample.public_visibility} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </AdminLayout>
  );
}
