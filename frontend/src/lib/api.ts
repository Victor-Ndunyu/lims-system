import { getApiBaseUrl, API_ENDPOINTS } from "./api-config";

function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") {
    return {};
  }
  const token = window.localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(path: string, options: RequestInit = {}) {
  const apiBase = getApiBaseUrl();
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  for (const [key, value] of Object.entries(getAuthHeaders())) {
    headers.set(key, value);
  }
  const response = await fetch(`${apiBase}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail || response.statusText || "Request failed");
  }
  return response.json();
}

async function publicRequest(path: string, options: RequestInit = {}) {
  const apiBase = getApiBaseUrl();
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  const response = await fetch(`${apiBase}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });
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
  return request(API_ENDPOINTS.AUTH_LOGIN, { method: "POST", body: JSON.stringify({ email, password }) });
}

export async function logout() {
  return request(API_ENDPOINTS.AUTH_LOGOUT, { method: "POST" });
}

export async function fetchCurrentUser() {
  return request(API_ENDPOINTS.AUTH_ME);
}

export async function changePassword(oldPassword: string, newPassword: string) {
  return request(API_ENDPOINTS.AUTH_CHANGE_PASSWORD, {
    method: "POST",
    body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
  });
}

export async function fetchMyPermissions() {
  return request(API_ENDPOINTS.STAFF_MY_PERMISSIONS);
}

export async function fetchAdminStats(): Promise<AdminStats> {
  return request(API_ENDPOINTS.ADMIN_STATS);
}

export async function fetchAdminCharts(): Promise<AdminCharts> {
  return request(API_ENDPOINTS.ADMIN_CHARTS);
}

export async function fetchAdminUsers(): Promise<AdminUser[]> {
  return request(API_ENDPOINTS.ADMIN_USERS);
}

export async function fetchAdminRoles(): Promise<RoleRead[]> {
  return request(API_ENDPOINTS.ADMIN_ROLES);
}

export async function fetchAdminPermissions(): Promise<PermissionRead[]> {
  return request(API_ENDPOINTS.ADMIN_PERMISSIONS);
}

export async function assignPermissionsToRole(roleId: string, permissionKeys: string[]) {
  return request(API_ENDPOINTS.ADMIN_ROLE_PERMISSIONS(roleId), {
    method: "POST",
    body: JSON.stringify(permissionKeys),
  });
}
export async function createAdminUser(payload: { full_name: string; email: string; password: string; role_name?: string }) {
  return request(API_ENDPOINTS.ADMIN_USERS, { method: "POST", body: JSON.stringify(payload) });
}

export async function updateAdminUser(userId: string, payload: { role_name?: string; is_active?: boolean }) {
  return request(API_ENDPOINTS.ADMIN_USER_BY_ID(userId), { method: "PATCH", body: JSON.stringify(payload) });
}

export async function deleteAdminUser(userId: string) {
  return request(API_ENDPOINTS.ADMIN_USER_BY_ID(userId), { method: "DELETE" });
}

export async function fetchSamples(status?: string) {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request(`${API_ENDPOINTS.STAFF_SAMPLES}${query}`);
}

export async function fetchStaffLookups() {
  return request(API_ENDPOINTS.STAFF_LOOKUPS);
}

export async function createSample(payload: unknown) {
  return request(API_ENDPOINTS.STAFF_SAMPLES, { method: "POST", body: JSON.stringify(payload) });
}

export async function updateSample(sampleId: string, payload: unknown) {
  return request(API_ENDPOINTS.STAFF_SAMPLE_BY_ID(sampleId), { method: "PUT", body: JSON.stringify(payload) });
}

export async function reviewSample(sampleId: string, payload: unknown) {
  return request(API_ENDPOINTS.STAFF_SAMPLE_REVIEW(sampleId), { method: "POST", body: JSON.stringify(payload) });
}

export async function fetchSample(sampleId: string) {
  return request(API_ENDPOINTS.STAFF_SAMPLE_BY_ID(sampleId));
}

export async function fetchPublicSamples() {
  return publicRequest(API_ENDPOINTS.PUBLIC_SAMPLES);
}

export type PublicStats = {
  total_samples: number;
  published_records: number;
  pending_approvals: number;
  total_locations: number;
  records_by_status: Array<{ status: string; count: number }>;
};

export async function fetchPublicStats(): Promise<PublicStats> {
  return publicRequest(API_ENDPOINTS.PUBLIC_STATS);
}

export async function uploadFile(file: File) {
  const apiBase = getApiBaseUrl();
  const formData = new FormData();
  formData.append("file", file);
  const headers = new Headers(getAuthHeaders());
  const response = await fetch(`${apiBase}${API_ENDPOINTS.STAFF_UPLOAD}`, {
    method: "POST",
    headers,
    body: formData,
    credentials: "include",
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail || "Upload failed");
  }
  return response.json() as Promise<{ file_name: string; file_type: string; file_url: string }>;
}

export async function createLocation(payload: {
  country: string;
  county?: string;
  subcounty?: string;
  site_name?: string;
  latitude?: number;
  longitude?: number;
  altitude?: number;
}) {
  return request(API_ENDPOINTS.STAFF_LOCATIONS, { method: "POST", body: JSON.stringify(payload) });
}

export async function reverseGeocode(lat: number, lng: number) {
  return request(`${API_ENDPOINTS.STAFF_GEOCODE}?lat=${lat}&lng=${lng}`);
}

export async function createSampleType(name: string) {
  return request(`${API_ENDPOINTS.STAFF_SAMPLE_TYPES}?name=${encodeURIComponent(name)}`, { method: "POST" });
}
