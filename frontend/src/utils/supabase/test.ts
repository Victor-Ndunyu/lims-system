/**
 * DEPRECATED: Direct Supabase browser queries removed for security
 * 
 * ❌ REASON: Direct database queries from the browser bypass backend authorization
 * 
 * ✅ PROPER APPROACH: Use backend API instead
 * 
 * All database queries should go through the FastAPI backend:
 * - Frontend calls: https://lims-system-vogc.onrender.com/api/*
 * - Backend validates: Authentication, Authorization, Permissions
 * - Backend queries: Supabase with service-role credentials
 * - Returns: Filtered data per user role
 * 
 * This ensures:
 * 1. Access control is enforced (no bypassing)
 * 2. Audit trails are maintained
 * 3. Business logic is centralized
 * 4. Secrets (service-role keys) stay backend-only
 * 
 * See: frontend/src/lib/api.ts for proper API client implementation
 */

async function testBackendConnection() {
  try {
    // Test backend health endpoint instead of direct DB
    const response = await fetch('https://lims-system-vogc.onrender.com/health', {
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) {
      return { success: false, error: `Backend returned ${response.status}` };
    }

    const data = await response.json();
    console.log('✓ Backend connection successful');
    console.log('Data:', data);
    return { success: true, data };
  } catch (err) {
    console.error('Error testing backend connection:', err);
    return { 
      success: false, 
      error: err instanceof Error ? err.message : 'Unknown error' 
    };
  }
}

export default testBackendConnection;
