/**
 * Core API utilities and configuration
 * Base layer for all API calls
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * Base API call function with automatic token injection
 * Handles authentication headers and error responses
 *
 * @param endpoint - API endpoint path (e.g. '/auth/login/')
 * @param options - Fetch options (method, body, custom headers)
 * @returns Parsed JSON response
 */
export async function apiCall(endpoint: string, options: RequestInit = {}) {
  const accessToken = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (typeof options.headers === 'object' && options.headers !== null && !(options.headers instanceof Headers)) {
    Object.assign(headers, options.headers);
  }

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}
