import { useState } from "react";
import { PageShell, Alert, Button } from "../../components/ui";
import { useRequireAuth } from "../../lib/useRequireAuth";
import { changePassword } from "../../lib/api";

export default function StaffSettings() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useRequireAuth();

  const handleChangePassword = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    if (!oldPassword || !newPassword || !confirmPassword) {
      setError("All fields are required.");
      return;
    }
    if (newPassword.length < 8) {
      setError("New password must be at least 8 characters.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("New passwords do not match.");
      return;
    }

    setSaving(true);
    try {
      await changePassword(oldPassword, newPassword);
      setSuccess("Password changed successfully.");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to change password.");
    }
    setSaving(false);
  };

  return (
    <PageShell wide>
      <section className="page-title">
        <p className="eyebrow">Account</p>
        <h1>Settings</h1>
        <p>Update your password and manage your account preferences.</p>
      </section>

      {error && <Alert tone="error">{error}</Alert>}
      {success && <Alert tone="success">{success}</Alert>}

      <form onSubmit={handleChangePassword} className="section form-card" style={{ maxWidth: 480 }}>
        <div className="section-header">
          <div>
            <p className="eyebrow">Security</p>
            <h2>Change password</h2>
          </div>
        </div>

        <div className="form-grid">
          <div className="field field-full">
            <label htmlFor="old_password">Current password</label>
            <input id="old_password" type="password" value={oldPassword} onChange={(e) => setOldPassword(e.target.value)} />
          </div>
          <div className="field field-full">
            <label htmlFor="new_password">New password</label>
            <input id="new_password" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
          </div>
          <div className="field field-full">
            <label htmlFor="confirm_password">Confirm new password</label>
            <input id="confirm_password" type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
          </div>
        </div>

        <div className="action-row" style={{ marginTop: 28 }}>
          <Button type="submit" disabled={saving}>
            {saving ? "Updating…" : "Change password"}
          </Button>
        </div>
      </form>
    </PageShell>
  );
}