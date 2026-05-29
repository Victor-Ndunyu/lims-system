import { useRouter } from "next/router";
import { useEffect, useState, type FormEvent } from "react";
import { PageShell, Button } from "../components/ui";
import { login } from "../lib/api";
import { getStoredUser, isAdminRole, storeAuth } from "../lib/session";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const existingUser = getStoredUser();
    if (existingUser) {
      router.replace(isAdminRole(existingUser.role_name) ? "/admin" : "/operations");
    }
  }, [router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await login(email, password);
      if (!response.access_token || !response.user) {
        throw new Error("Unexpected login response");
      }
      storeAuth(response.access_token, response.user);
      router.replace(isAdminRole(response.user.role_name) ? "/admin" : "/operations");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <PageShell wide>
      <section className="page-title">
        <div>
          <p className="eyebrow">Staff sign in</p>
          <h1>Sign in to your account</h1>
          <p>Enter your credentials to access the operations workspace.</p>
        </div>
      </section>

      <section className="section card login-card">
        <form onSubmit={handleSubmit} className="form-grid">
          {error && <div className="alert alert-error">{error}</div>}

          <label className="form-field">
            <span>Email address</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              placeholder="you@example.com"
            />
          </label>

          <label className="form-field">
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              placeholder="Enter your password"
            />
          </label>

          <div className="form-actions">
            <Button type="submit" tone="primary">{isSubmitting ? "Signing in…" : "Sign in"}</Button>
          </div>
        </form>
      </section>
    </PageShell>
  );
}
