import Link from "next/link";

export default function AdminHome() {
  return (
    <main style={{ padding: 24, fontFamily: "Arial, sans-serif" }}>
      <h1>Admin Portal</h1>
      <p>This interface is reserved for authenticated staff and requires role-based access.</p>
      <Link href="/">Back to home</Link>
    </main>
  );
}
