/**
 * Barcode processing API endpoints
 * Handles barcode image processing and detection
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

export interface ItemData {
  id: number;
  barcode: string;
  title: string;
  description: string;
  alias: string;
  brand: number | null;
}
