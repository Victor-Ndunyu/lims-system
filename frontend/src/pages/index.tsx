import { ButtonLink, PageShell, StatCard, StatusBadge } from "../components/ui";

export default function Home() {
  return (
    <PageShell wide>
      <section className="hero">
        <div>
          <p className="eyebrow">Animal health surveillance platform</p>
          <h1>Field sample intelligence for serious veterinary research.</h1>
          <p>
            A secure data platform for tracking field samples, laboratory review, and public release of verified animal-health
            surveillance records across field and diagnostic workflows.
          </p>
          <div className="hero-actions">
            <ButtonLink href="/public">Explore public records</ButtonLink>
            <ButtonLink href="/admin" tone="secondary">
              Open admin workspace
            </ButtonLink>
          </div>
        </div>
        <div className="hero-visual" aria-label="Animal health sample surveillance dashboard preview">
          <div className="wave-panel">
            <p className="eyebrow">Diagnostic signal</p>
            <h3>Sample integrity monitor</h3>
            <div className="wave-line" />
            <div className="grid grid-2">
              <StatCard label="Verified records" value="128" note="Approved for release" />
              <StatCard label="Coverage" value="14" note="Field collection zones" />
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="kpi-strip">
          <StatCard label="Sample records" value="1,248" note="Tracked across field teams" />
          <StatCard label="Locations" value="42" note="Active surveillance sites" />
          <StatCard label="Review queue" value="18" note="Awaiting scientific validation" />
          <StatCard label="Published" value="312" note="Read-only public records" />
        </div>
      </section>

      <section className="section grid grid-2">
        <article className="card micro-grid">
          <p className="eyebrow">Trusted workflow</p>
          <h2>From collection to verified publication</h2>
          <p className="muted">
            The platform separates field entry, reviewer decisions, audit history, and public visibility so each sample moves
            through a controlled surveillance pipeline.
          </p>
          <div className="action-row" style={{ marginTop: 20 }}>
            <StatusBadge status="Draft" />
            <StatusBadge status="Submitted" />
            <StatusBadge status="Approved" />
            <StatusBadge status="Published" />
          </div>
        </article>
        <article className="card map-panel">
          <p className="eyebrow">Spatial intelligence</p>
          <h2>Coverage designed for field epidemiology</h2>
          <p className="muted">
            Structured sample, site, collector, and review metadata supports surveillance reporting, diagnostics coordination,
            and transparent public communication.
          </p>
        </article>
      </section>

      <section className="section">
        <div className="section-header">
          <div>
            <p className="eyebrow">Operational summary</p>
            <h2>Built for animal health organizations</h2>
            <p>Clean portals for different audiences, one consistent source of truth.</p>
          </div>
        </div>
        <div className="grid grid-3">
          <article className="card">
            <h3>Public scientific portal</h3>
            <p className="muted">Read-only access to approved records, with clear status and collection metadata.</p>
          </article>
          <article className="card">
            <h3>Admin operations</h3>
            <p className="muted">Efficient sample management, role-based workflows, and reviewer decisions.</p>
          </article>
          <article className="card">
            <h3>Audit confidence</h3>
            <p className="muted">Versioned records and audit logs help preserve scientific traceability.</p>
          </article>
        </div>
      </section>
    </PageShell>
  );
}
