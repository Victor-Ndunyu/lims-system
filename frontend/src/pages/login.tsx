import { useRouter } from "next/router";
import { useEffect, useState, type FormEvent } from "react";
import { PageShell, Alert, Button } from "../components/ui";
import { login, resetPassword } from "../lib/api";
import { getStoredUser, isAdminRole, storeAuth } from "../lib/session";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [resetEmail, setResetEmail] = useState("");
  const [resetPasswordValue, setResetPasswordValue] = useState("");
  const [resetConfirmPassword, setResetConfirmPassword] = useState("");
  const [resetError, setResetError] = useState<string | null>(null);
  const [resetSuccess, setResetSuccess] = useState<string | null>(null);
  const [isResetting, setIsResetting] = useState(false);

  useEffect(() => {
    const existingUser = getStoredUser();
    if (existingUser) {
      router.replace(isAdminRole(existingUser.role_name) ? "/admin" : "/staff");
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
      router.replace(isAdminRole(response.user.role_name) ? "/admin" : "/staff");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
      setShowForgotPassword(true);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleResetPassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setResetError(null);
    setResetSuccess(null);

    if (!resetEmail || !resetPasswordValue || !resetConfirmPassword) {
      setResetError("All fields are required.");
      return;
    }
    if (resetPasswordValue.length < 8) {
      setResetError("New password must be at least 8 characters.");
      return;
    }
    if (resetPasswordValue !== resetConfirmPassword) {
      setResetError("Passwords do not match.");
      return;
    }

    setIsResetting(true);
    try {
      await resetPassword(resetEmail, resetPasswordValue);
      setResetSuccess("Password reset successfully. You can now sign in.");
      setShowForgotPassword(false);
      setEmail(resetEmail);
    } catch (err) {
      setResetError(err instanceof Error ? err.message : "Failed to reset password.");
    }
    setIsResetting(false);
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
        {!showForgotPassword ? (
          <form onSubmit={handleSubmit} className="form-grid">
            {error && <Alert tone="error">{error}</Alert>}

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
        ) : (
          <form onSubmit={handleResetPassword} className="form-grid">
            {resetError && <Alert tone="error">{resetError}</Alert>}
            {resetSuccess && <Alert tone="success">{resetSuccess}</Alert>}
            {error && !resetError && <Alert tone="error">{error}</Alert>}

            <p style={{ margin: 0, fontSize: "0.88rem" }}>Enter your email and a new password to reset your account password.</p>

            <label className="form-field">
              <span>Email address</span>
              <input
                type="email"
                value={resetEmail}
                onChange={(event) => setResetEmail(event.target.value)}
                required
                placeholder="you@example.com"
              />
            </label>

            <label className="form-field">
              <span>New password</span>
              <input
                type="password"
                value={resetPasswordValue}
                onChange={(event) => setResetPasswordValue(event.target.value)}
                required
                placeholder="At least 8 characters"
              />
            </label>

            <label className="form-field">
              <span>Confirm new password</span>
              <input
                type="password"
                value={resetConfirmPassword}
                onChange={(event) => setResetConfirmPassword(event.target.value)}
                required
                placeholder="Re-enter new password"
              />
            </label>

            <div className="form-actions" style={{ flexDirection: "column", gap: "var(--space-3)" }}>
              <Button type="submit" tone="primary" disabled={isResetting}>
                {isResetting ? "Resetting…" : "Reset password"}
              </Button>
              <button type="button" className="button button-ghost" onClick={() => { setShowForgotPassword(false); setError(null); }}>
                Back to sign in
              </button>
            </div>
          </form>
        )}
      </section>
    </PageShell>
  );
}