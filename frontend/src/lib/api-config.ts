/**
 * Central API Configuration Module
 *
 * Provides a single source of truth for API base URLs for Next.js.
 * Uses Next.js environment variables (process.env.NEXT_PUBLIC_*).
 *
 * REQUIRED Environment Variables:
 * - NEXT_PUBLIC_API_URL: Full API base URL (e.g., https://api.example.com)
 *   Must be set in production (Vercel environment variables)
 *   Must be set in development (.env.local)
 *
 * No secrets are exposed in this module - only public configuration.
 */

/**
 * Get the API base URL from Next.js environment variables
 *
 * REQUIRED: NEXT_PUBLIC_API_URL must be set in all environments
 * - Development: Use .env.local (e.g., http://localhost:8000)
 * - Production: Set in Vercel dashboard (e.g., https://api.example.com)
 *
 * @throws Error if NEXT_PUBLIC_API_URL is not set in production
 */
export function getApiBaseUrl(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  // Production safety check
  if (!apiUrl && typeof window !== "undefined" && process.env.NODE_ENV === "production") {
    throw new Error(
      "NEXT_PUBLIC_API_URL environment variable is not set. " +
      "Set it in Vercel dashboard → Settings → Environment Variables with the backend URL."
    );
  }

  // Fallback for development if not set (should still be set)
  if (!apiUrl && process.env.NODE_ENV === "development") {
    console.warn(
      "[API Config] NEXT_PUBLIC_API_URL not set. Using /api fallback. " +
      "Please set NEXT_PUBLIC_API_URL in .env.local for external backend."
    );
    return "/api";
  }

  return apiUrl || "/api";
}

/**
 * Validate API configuration at build time and runtime
 */
export function validateApiConfig(): void {
  // Only validate on client-side
  if (typeof window === "undefined") {
    return;
  }

  try {
    const apiUrl = getApiBaseUrl();

    // Development logging
    if (process.env.NODE_ENV === "development") {
      console.debug(`[API Config] Using API Base URL: ${apiUrl}`);
    }
  } catch (error) {
    // In production, log the error for visibility
    if (process.env.NODE_ENV === "production") {
      console.error("[API Config] Configuration error:", error);
    }
  }
}

// Validate on module load (client-side only)
if (typeof window !== "undefined") {
  validateApiConfig();
}

/**
 * API endpoints used throughout the application
 * All paths include /api prefix since backend routes are under app.include_router(api_router, prefix="/api")
 */
export const API_ENDPOINTS = {
  // Authentication
  AUTH_LOGIN: "/api/auth/login",
  AUTH_LOGOUT: "/api/auth/logout",
  AUTH_ME: "/api/auth/me",
  AUTH_CHANGE_PASSWORD: "/api/auth/change-password",

  // Admin operations
  ADMIN_STATS: "/api/admin/stats",
  ADMIN_CHARTS: "/api/admin/charts",
  ADMIN_USERS: "/api/admin/users",
  ADMIN_ROLES: "/api/admin/roles",
  ADMIN_PERMISSIONS: "/api/admin/permissions",
  ADMIN_ROLE_PERMISSIONS: (roleId: string) => `/api/admin/roles/${roleId}/permissions`,
  ADMIN_USER_BY_ID: (userId: string) => `/api/admin/users/${userId}`,

  // Staff operations
  STAFF_SAMPLES: "/api/staff/samples",
  STAFF_MY_PERMISSIONS: "/api/staff/my-permissions",
  STAFF_SAMPLE_BY_ID: (id: string) => `/api/staff/samples/${id}`,
  STAFF_SAMPLE_REVIEW: (id: string) => `/api/staff/samples/${id}/review`,
  STAFF_LOOKUPS: "/api/staff/lookups",
  STAFF_UPLOAD: "/api/staff/upload",
  STAFF_LOCATIONS: "/api/staff/locations",
  STAFF_GEOCODE: "/api/staff/geocode",
  STAFF_SAMPLE_TYPES: "/api/staff/sample-types",

  // Public operations
  PUBLIC_SAMPLES: "/api/public/samples",
  PUBLIC_STATS: "/api/public/stats",
} as const;
