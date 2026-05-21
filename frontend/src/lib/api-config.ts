/**
 * Central API Configuration Module
 *
 * Provides a single source of truth for API base URLs for Next.js.
 * Uses Next.js environment variables (process.env.NEXT_PUBLIC_*).
 *
 * Environment Variables:
 * - NEXT_PUBLIC_API_URL: Full API base URL (e.g., http://localhost:8000 or https://api.example.com)
 * - Falls back to /api for relative URLs (works with same-origin proxy or API route)
 *
 * No secrets are exposed in this module - only public configuration.
 */

/**
 * Get the API base URL from Next.js environment variables or defaults
 *
 * Priority:
 * 1. process.env.NEXT_PUBLIC_API_URL (Next.js public env var)
 * 2. "/api" (relative fallback)
 */
export function getApiBaseUrl(): string {
  // Next.js public environment variable (available at build time and runtime)
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // Fallback to relative URL (works with same-origin proxy or API routes)
  return "/api";
}

/**
 * Validate API configuration at runtime (development only)
 */
export function validateApiConfig(): void {
  if (typeof window === "undefined") {
    return; // Skip server-side validation
  }

  const apiUrl = getApiBaseUrl();

  // Warn in development if using default fallback
  if (apiUrl === "/api" && process.env.NODE_ENV === "development") {
    console.warn(
      "[API Config] Using relative /api URL. Set NEXT_PUBLIC_API_URL if calling external API server.",
    );
  }

  // Log in development
  if (process.env.NODE_ENV === "development") {
    console.debug(`[API Config] API Base URL: ${apiUrl}`);
  }
}

// Validate on module load
validateApiConfig();

/**
 * API endpoints used throughout the application
 * All use the centralized API base URL
 */
export const API_ENDPOINTS = {
  // Authentication
  AUTH_LOGIN: "/auth/login",
  AUTH_LOGOUT: "/auth/logout",
  AUTH_ME: "/auth/me",

  // Admin operations
  ADMIN_STATS: "/admin/stats",
  ADMIN_CHARTS: "/admin/charts",
  ADMIN_USERS: "/admin/users",
  ADMIN_ROLES: "/admin/roles",
  ADMIN_PERMISSIONS: "/admin/permissions",
  ADMIN_ROLE_PERMISSIONS: (roleId: string) => `/admin/roles/${roleId}/permissions`,

  // Staff operations
  STAFF_SAMPLES: "/staff/samples",
  STAFF_SAMPLE_BY_ID: (id: string) => `/staff/samples/${id}`,
  STAFF_SAMPLE_REVIEW: (id: string) => `/staff/samples/${id}/review`,
  STAFF_LOOKUPS: "/staff/lookups",

  // Public operations
  PUBLIC_SAMPLES: "/public/samples",
} as const;
