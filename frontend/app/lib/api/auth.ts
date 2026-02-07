/**
 * Authentication API endpoints and utilities
 * Handles user registration, login, profile management, and token storage
 */

import { apiCall, API_BASE_URL } from './core';

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface User {
  id: number;
  email: string;
}

/**
 * Register a new user account
 *
 * @param email - User email address
 * @param password - User password
 * @param passwordConfirm - Password confirmation
 * @returns New user object
 */
export async function register(
  email: string,
  password: string,
  passwordConfirm: string
): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/auth/register/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
      password_confirm: passwordConfirm,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || JSON.stringify(error));
  }

  return response.json();
}

/**
 * Log in with email and password
 *
 * @param email - User email address
 * @param password - User password
 * @returns Auth tokens (access and refresh)
 */
export async function login(email: string, password: string): Promise<AuthTokens> {
  const response = await fetch(`${API_BASE_URL}/auth/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || JSON.stringify(error));
  }

  return response.json();
}

/**
 * Fetch the current user's profile
 *
 * @returns Current user object
 */
export async function getProfile(): Promise<User> {
  return apiCall('/auth/profile/');
}

/**
 * Update the current user's profile
 *
 * @param email - New email address
 * @returns Updated user object
 */
export async function updateProfile(email: string): Promise<User> {
  return apiCall('/auth/profile/', {
    method: 'PUT',
    body: JSON.stringify({ email }),
  });
}

/**
 * Store auth tokens in localStorage and cookies
 * localStorage enables offline-first approach and automatic token injection
 * cookies enable middleware to access tokens for auth redirects
 *
 * @param tokens - Auth tokens from login/register
 */
export function setTokens(tokens: AuthTokens) {
  if (typeof window !== 'undefined') {
    // Store in localStorage for client-side access
    localStorage.setItem('accessToken', tokens.access);
    localStorage.setItem('refreshToken', tokens.refresh);

    // Store in cookies for middleware access (secure auth redirects)
    document.cookie = `accessToken=${tokens.access}; path=/; max-age=3600`;
    document.cookie = `refreshToken=${tokens.refresh}; path=/; max-age=604800`;
  }
}

/**
 * Retrieve the access token from localStorage
 *
 * @returns Access token or null if not authenticated
 */
export function getAccessToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('accessToken');
  }
  return null;
}

/**
 * Clear all auth tokens from localStorage and cookies
 * Effectively logs the user out
 */
export function clearTokens() {
  if (typeof window !== 'undefined') {
    // Clear localStorage
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');

    // Clear cookies (set with max-age=0 to delete)
    document.cookie = 'accessToken=; path=/; max-age=0';
    document.cookie = 'refreshToken=; path=/; max-age=0';
  }
}
