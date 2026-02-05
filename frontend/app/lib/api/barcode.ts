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
 * TODO: FUTURE IMPLEMENTATION - UPC Database Lookup
 *
 * Once implemented, this function will fetch product information from the UPC Database API.
 *
 * API: https://upcdatabase.org/api/json/{barcode}
 *
 * Example implementation:
 *
 * export async function lookupProductByUPC(barcode: string): Promise<UPCProduct> {
 *   try {
 *     const response = await fetch(`https://upcdatabase.org/api/json/${barcode}`);
 *     if (!response.ok) throw new Error(`UPC lookup failed: ${response.statusText}`);
 *     return response.json();
 *   } catch (error) {
 *     console.error('Error looking up UPC:', error);
 *     throw error;
 *   }
 * }
 *
 * interface UPCProduct {
 *   valid: boolean;
 *   number: string;
 *   quantity: string;
 *   description: string;
 *   brand: string;
 *   title: string;
 *   reviews: string;
 *   category: string;
 *   size: string;
 * }
 */
