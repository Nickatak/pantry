/**
 * API module barrel exports
 * Re-exports all API functions from sub-modules for clean imports
 */

// Core utilities
export { apiCall, API_BASE_URL } from './core';

// Auth API
export {
  register,
  login,
  getProfile,
  updateProfile,
  setTokens,
  getAccessToken,
  clearTokens,
  type AuthTokens,
  type User,
} from './auth';

// Barcode API
export {
  processBarcodeImage,
  lookupItemByUPC,
  type ProcessBarcodeResult,
  type ItemData,
} from './barcode';
