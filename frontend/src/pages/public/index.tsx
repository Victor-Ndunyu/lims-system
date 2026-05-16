import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import { EmptyState, PageShell, StatCard, StatusBadge } from "../../components/ui";
import { fetchPublicSamples } from "../../lib/api";
import { SampleRow } from "../../types/sample";

export default function PublicHome() {
  const [samples, setSamples] = useState<SampleRow[]>([]);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("all");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPublicSamples()
      .then((data) => setSamples(data))
      .catch((err) => setError(err.message));
  }, []);

  const filteredSamples = useMemo(() => {
    return samples.filter((sample) => {
      const matchesQuery = `${sample.sample_code} ${sample.description || ""} ${sample.remarks || ""}`
        .toLowerCase()
        .includes(query.toLowerCase());
      const matchesStatus = status === "all" || sample.status === status;
      return matchesQuery && matchesStatus;
    });
  }, [query, samples, status]);

  return (
    <PageShell wide>
      <section className="page-title">
        <div>
          <p className="eyebrow">Public scientific portal</p>
          <h1>Verified animal-health sample records</h1>
          <p>Read-only access to approved surveillance data released for public reference.</p>
        </div>
        <StatusBadge status="Read only" />
      </section>

      <section className="kpi-strip">
        <StatCard label="Public records" value={String(samples.length)} note="Approved for visibility" />
        <StatCard label="Published" value={String(samples.filter((sample) => sample.public_visibility).length)} note="Visible records" />
        <StatCard label="Attachments" value={String(samples.reduce((total, sample) => total + (sample.attachments?.length || 0), 0))} note="Linked evidence files" />
        <StatCard label="Latest update" value={samples[0] ? new Date(samples[0].collection_date).toLocaleDateString() : "-"} note="Most recent collection" />
      </section>

      <section className="section">
        <div className="filter-bar">
          <input
            className="search-input"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search sample code, descriptions, or remarks"
            aria-label="Search public records"
          />
          <select className="search-input" value={status} onChange={(event) => setStatus(event.target.value)} aria-label="Filter by status">
            <option value="all">All statuses</option>
            <option value="Approved">Approved</option>
          </select>
          <Link className="button button-secondary" href="/">
            Platform overview
          </Link>
        </div>
      </section>

      {error && <div className="alert alert-error">{error}</div>}

      <section className="section record-list" aria-label="Public sample records">
        {filteredSamples.length === 0 ? (
          <EmptyState title="No public records match this view" message="Approved records will appear here after scientific review and publication." />
        ) : (
          filteredSamples.map((sample) => (
            <article className="public-record-card" key={sample.id}>
              <div>
                <p className="eyebrow">Sample record</p>
                <h2 style={{ margin: 0 }}>{sample.sample_code}</h2>
                <p className="muted">{sample.description || sample.remarks || "Verified animal-health sample record."}</p>
                <div className="record-meta">
                  <span>Collected {new Date(sample.collection_date).toLocaleDateString()}</span>
                  <span>{sample.attachments?.length || 0} evidence files</span>
                  <span>Record ID {sample.id.slice(0, 8)}</span>
                </div>
              </div>
              <div className="action-row" style={{ justifyContent: "flex-end" }}>
                <StatusBadge status={sample.status} />
                <StatusBadge status={sample.public_visibility} />
              </div>
            </article>
          ))
        )}
      </section>
    </PageShell>
  );
}
