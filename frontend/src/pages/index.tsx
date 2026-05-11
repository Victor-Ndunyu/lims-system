import Link from "next/link";

export default function Home() {
  return (
    <main style={{ padding: 24, fontFamily: "Arial, sans-serif" }}>
      <h1>Field Sample Management</h1>
      <p>Separate public and admin interfaces are scaffolded.</p>
      <ul>
        <li>
          <Link href="/public">Public portal (read-only)</Link>
        </li>
        <li>
          <Link href="/admin">Admin portal (authentication required)</Link>
        </li>
      </ul>
    </main>
  );
}
