import { useRouter } from "next/router";
import { useEffect, useState, type FormEvent } from "react";
import { AdminLayout, Alert, Button } from "../../../components/ui";
import { createAdminUser, fetchAdminRoles, type RoleRead } from "../../../lib/api";
import { useRequireRole } from "../../../lib/useRequireAuth";

export default function NewAdminUserPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [roleName, setRoleName] = useState("");
  const [roles, setRoles] = useState<RoleRead[]>([]);
  const [loadingRoles, setLoadingRoles] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useRequireRole("admin");

  useEffect(() => {
    fetchAdminRoles()
      .then((data) => {
        setRoles(data);
        if (data.length > 0) {
          setRoleName(data[0].role_name);
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoadingRoles(false));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await createAdminUser({ full_name: fullName, email, password, role_name: roleName });
      router.replace("/admin/users");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create user");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AdminLayout active="users">
      <section className="page-title">
        <div>
          <p className="eyebrow">Invite staff</p>
          <h1>Create a new platform user</h1>
          <p>Register staff accounts and assign them the correct role for sample and review workflows.</p>
        </div>
      </section>

      <section className="section card">
        <form onSubmit={handleSubmit} className="form-grid">
          {error && <Alert tone="error">{error}</Alert>}

          <label className="form-field">
            <span>Full name</span>
            <input value={fullName} onChange={(event) => setFullName(event.target.value)} required placeholder="Jane Doe" />
          </label>

          <label className="form-field">
            <span>Email address</span>
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required placeholder="jane.doe@example.com" />
          </label>

          <label className="form-field">
            <span>Password</span>
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required placeholder="Choose a strong password" />
          </label>

          <label className="form-field">
            <span>Role</span>
            {loadingRoles ? (
              <p className="muted">Loading roles…</p>
            ) : (
              <select value={roleName} onChange={(event) => setRoleName(event.target.value)}>
                {roles.map((role) => (
                  <option key={role.id} value={role.role_name}>
                    {role.role_name.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            )}
          </label>

          <div className="form-actions">
            <Button type="submit" tone="primary">{isSubmitting ? "Creating user…" : "Create user"}</Button>
          </div>
        </form>
      </section>
    </AdminLayout>
  );
}
