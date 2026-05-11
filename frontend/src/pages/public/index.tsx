import Link from "next/link";

export default function PublicHome() {
  return (
    <main style={{ padding: 24, fontFamily: "Arial, sans-serif" }}>
      <h1>Public Portal</h1>
      <p>This interface is read-only and shows approved public records only.</p>
      <Link href="/">Back to home</Link>
    </main>
  );
}
