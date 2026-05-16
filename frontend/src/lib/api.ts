const API_BASE = process.env.NEXT_PUBLIC_ADMIN_API_URL || "/api";
const PUBLIC_API_BASE = process.env.NEXT_PUBLIC_PUBLIC_API_URL || API_BASE;

function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") {
    return {};
  }
  const token = window.localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(path: string, options: RequestInit = {}) {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  for (const [key, value] of Object.entries(getAuthHeaders())) {
    headers.set(key, value);
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail || response.statusText || "Request failed");
  }
  return response.json();
}

async function publicRequest(path: string, options: RequestInit = {}) {
  const response = await fetch(`${PUBLIC_API_BASE}${path}`, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail || response.statusText || "Request failed");
  }
  return response.json();
}

export type UserSession = {
  id: string;
  full_name: string;
  email: string;
  role_name?: string;
  is_active: boolean;
};

export type AdminStats = {
  total_users: number;
  active_users: number;
  inactive_users: number;
  records_submitted_today: number;
  pending_approvals: number;
  published_records: number;
  recent_activity: Array<{ action: string; table: string; performed_by: string | null; at: string }>;
};

export type AdminCharts = {
  records_by_status: Array<{ status: string; count: number }>;
  records_by_type: Array<{ sample_type_id: string; count: number }>;
  users_by_role: Array<{ role: string; count: number }>;
};

export type PermissionRead = {
  id: string;
  permission_key: string;
  description?: string;
};

export type RoleRead = {
  id: string;
  role_name: string;
  description?: string;
  permissions?: PermissionRead[];
};

export type AdminUser = {
  id: string;
  full_name: string;
  email: string;
  role_name?: string;
  is_active: boolean;
};

export async function login(email: string, password: string) {
  return request(`/auth/login`, { method: "POST", body: JSON.stringify({ email, password }) });
}

export async function logout() {
  return request(`/auth/logout`, { method: "POST" });
}

export async function fetchCurrentUser() {
  return request(`/auth/me`);
}

export async function fetchAdminStats(): Promise<AdminStats> {
  return request(`/admin/stats`);
}

export async function fetchAdminCharts(): Promise<AdminCharts> {
  return request(`/admin/charts`);
}

export async function fetchAdminUsers(): Promise<AdminUser[]> {
  return request(`/admin/users`);
}

export async function fetchAdminRoles(): Promise<RoleRead[]> {
  return request(`/admin/roles`);
}

export async function fetchAdminPermissions(): Promise<PermissionRead[]> {
  return request(`/admin/permissions`);
}

export async function assignPermissionsToRole(roleId: string, permissionKeys: string[]) {
  return request(`/admin/roles/${roleId}/permissions`, {
    method: "POST",
    body: JSON.stringify(permissionKeys),
  });
}
export async function createAdminUser(payload: { full_name: string; email: string; password: string; role_name?: string }) {
  return request(`/admin/users`, { method: "POST", body: JSON.stringify(payload) });
}

export async function fetchSamples(status?: string) {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request(`/staff/samples${query}`);
}

export async function fetchStaffLookups() {
  return request(`/staff/lookups`);
}

export async function createSample(payload: unknown) {
  return request(`/staff/samples`, { method: "POST", body: JSON.stringify(payload) });
}

export async function updateSample(sampleId: string, payload: unknown) {
  return request(`/staff/samples/${sampleId}`, { method: "PUT", body: JSON.stringify(payload) });
}

export async function reviewSample(sampleId: string, payload: unknown) {
  return request(`/staff/samples/${sampleId}/review`, { method: "POST", body: JSON.stringify(payload) });
}

export async function fetchSample(sampleId: string) {
  return request(`/staff/samples/${sampleId}`);
}

export async function fetchPublicSamples() {
  return publicRequest(`/public/samples`);
}
