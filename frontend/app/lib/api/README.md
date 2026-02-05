/**
 * API MODULE STRUCTURE
 *
 * This module is organized by API domain/concern:
 *
 * ├── core.ts
 * │   ├── API_BASE_URL - API base configuration
 * │   └── apiCall() - Core API call function with auth
 * │
 * ├── auth.ts
 * │   ├── register() - User registration
 * │   ├── login() - User login
 * │   ├── getProfile() - Fetch current user
 * │   ├── updateProfile() - Update user profile
 * │   ├── setTokens() - Store tokens in localStorage
 * │   ├── getAccessToken() - Retrieve access token
 * │   ├── clearTokens() - Clear all tokens (logout)
 * │   ├── AuthTokens - Interface for auth tokens
 * │   └── User - Interface for user object
 * │
 * ├── barcode.ts
 * │   ├── processBarcodeImage() - Process barcode image
 * │   └── ProcessBarcodeResult - Interface for result
 * │
 * └── index.ts
 *     └── Barrel exports for clean imports
 *
 * IMPORT PATTERNS:
 *
 * // Default import style (recommended) - gets everything
 * import { login, setTokens } from '../lib/api';
 *
 * // Specific module import - if you need direct access
 * import { login } from '../lib/api/auth';
 * import { processBarcodeImage } from '../lib/api/barcode';
 *
 * BENEFITS:
 * ✓ Clear separation of concerns
 * ✓ Easy to find related functions
 * ✓ Single domain responsibility
 * ✓ Easier to expand (add new domains)
 * ✓ Better code organization
 * ✓ Testability - can mock individual modules
 */
