/**
 * Barcode processing and item management API endpoints
 *
 * Two-step item creation workflow:
 * 1. Scan barcode → processBarcodeImage() → extract UPC code
 * 2. Lookup product → lookupProductByUPC() → get external product data (may fail)
 * 3. Create item → createItem() → save to database with user-provided data
 */

import { apiCall } from './core';

export interface ProcessBarcodeResult {
  detected: boolean;
  barcode_code?: string;
}

/**
 * Send a barcode image to the backend for processing
 * Extracts the barcode code from the image
 *
 * @param imageData - Base64 encoded JPEG image (without data URL prefix)
 * @returns Result containing detection status and barcode code
 */
export async function processBarcodeImage(
  imageData: string
): Promise<{ barcode_code: string; detected: boolean }> {
  return apiCall('/barcode/process/', {
    method: 'POST',
    body: JSON.stringify({ image: imageData }),
  });
}

/**
 * Lookup item details by UPC from the backend database
 * Creates or retrieves item from database using UPC code
 *
 * @param upc - UPC/barcode code to lookup
 * @returns Item data from database including creation status
 */
export async function lookupItemByUPC(
  upc: string
): Promise<{
  created: boolean;
  item: ItemData;
  product_data: Record<string, unknown>;
}> {
  return apiCall(`/items/${upc}/`, {
    method: 'GET',
  });
}

/**
 * Lookup product data by UPC from external database
 * Does NOT create an item in the database - used for form pre-filling
 *
 * FLOW:
 * 1. Query external UPC database (upcdatabase.com)
 * 2. If found: return product data with title, description, brand, etc.
 * 3. If not found: throw error, allows user to manually add new UPC
 *
 * @param upc - UPC/barcode code to lookup
 * @returns Product data from external database
 * @throws Error if product not found in external database
 */
export async function lookupProductByUPC(
  upc: string
): Promise<{ product_data: Record<string, unknown> }> {
  return apiCall(`/items/lookup-product/${upc}/`, {
    method: 'GET',
  });
}

/**
 * Create a new item with the provided data
 * Saves item to local database with user-provided or edited information
 *
 * @param itemData - Item data to create {barcode, title, description, alias}
 * @returns Created item data including generated ID
 * @throws Error if validation fails or cannot save to database
 */
export async function createItem(itemData: {
  barcode: string;
  title: string;
  description: string;
  alias: string;
}): Promise<ItemData> {
  return apiCall('/items/create-from-upc/', {
    method: 'POST',
    body: JSON.stringify(itemData),
  });
}

export interface ItemData {
  id: number;
  barcode: string;
  title: string;
  description: string;
  alias: string;
  brand: number | null;
}
