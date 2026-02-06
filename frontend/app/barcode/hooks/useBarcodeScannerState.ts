/**
 * Hook for managing barcode scanner state and processing
 */

import { useRef, useState } from 'react';
import { processBarcodeImage, lookupItemByUPC, ItemData } from '../../lib/api/barcode';

/**
 * Manages barcode detection state and API processing
 *
 * FLOW:
 * - Tracks detected barcode code, item data, loading state, and last processed time
 * - Provides throttled processing to prevent multiple rapid requests
 * - Handles both manual capture and automatic detection
 * - Automatically fetches item data after successful barcode detection
 */
export const useBarcodeScannerState = () => {
  const [barcodeCode, setBarcodeCode] = useState<string | null>(null);
  const [itemData, setItemData] = useState<ItemData | null>(null);
  const [productData, setProductData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [lookupError, setLookupError] = useState<string | null>(null);
  const lastProcessedTimeRef = useRef<number>(0);

  /**
   * Sends manually captured video frame to backend for barcode processing,
   * then looks up item data from database.
   *
   * FLOW:
   * 1. Throttles to prevent multiple requests (2s cooldown)
   * 2. Captures current video frame as JPEG
   * 3. Sends to backend API for barcode detection
   * 4. If barcode detected, fetches item data from /api/items/{UPC}
   * 5. Stores both barcode code and item information
   * 6. API call errors are rethrown for caller to handle
   */
  const processDetectedBarcodeAsync = async (
    videoElement: HTMLVideoElement,
    canvasElement: HTMLCanvasElement
  ): Promise<boolean> => {
    // Throttle processing to prevent too many requests
    const now = Date.now();
    if (now - lastProcessedTimeRef.current < 2000) {
      return false;
    }
    lastProcessedTimeRef.current = now;

    try {
      setLoading(true);
      setLookupError(null);

      const context = canvasElement.getContext('2d');
      if (!context) throw new Error('Could not get canvas context');

      canvasElement.width = videoElement.videoWidth;
      canvasElement.height = videoElement.videoHeight;
      context.drawImage(videoElement, 0, 0);

      // Convert canvas to base64
      const imageData = canvasElement
        .toDataURL('image/jpeg')
        .split(',')[1];

      // Step 1: Send to backend for barcode processing
      const barcodeResult = await processBarcodeImage(imageData);

      if (barcodeResult.detected && barcodeResult.barcode_code) {
        setBarcodeCode(barcodeResult.barcode_code);

        // Step 2: Look up item data using UPC
        try {
          const itemLookup = await lookupItemByUPC(barcodeResult.barcode_code);
          setItemData(itemLookup.item);
          setProductData(itemLookup.product_data);
        } catch (itemError) {
          console.error('Error looking up item:', itemError);
          setLookupError(
            itemError instanceof Error ? itemError.message : 'Failed to lookup item'
          );
          // Still show the barcode even if item lookup fails
        }

        return true;
      }

      return false;
    } catch (err) {
      console.error('Error processing barcode:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fetch item data for an auto-detected barcode
   * Used when barcode is detected directly by html5qrcode library
   *
   * FLOW:
   * 1. Sets the barcode code
   * 2. Fetches item data from database
   * 3. Stores product information or error
   */
  const lookupItemByBarcodeAsync = async (barcode: string): Promise<void> => {
    try {
      setLoading(true);
      setLookupError(null);
      setBarcodeCode(barcode);

      // Look up item data using UPC
      try {
        const itemLookup = await lookupItemByUPC(barcode);
        setItemData(itemLookup.item);
        setProductData(itemLookup.product_data);
      } catch (itemError) {
        console.error('Error looking up item:', itemError);
        setLookupError(
          itemError instanceof Error ? itemError.message : 'Failed to lookup item'
        );
        // Still keep the barcode code even if item lookup fails
      }
    } catch (err) {
      console.error('Error processing detected barcode:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const resetState = () => {
    setBarcodeCode(null);
    setItemData(null);
    setProductData(null);
    setProcessing(false);
    setLookupError(null);
    lastProcessedTimeRef.current = 0;
  };

  return {
    barcodeCode,
    setBarcodeCode,
    itemData,
    productData,
    loading,
    setLoading,
    processing,
    setProcessing,
    lookupError,
    processDetectedBarcodeAsync,
    lookupItemByBarcodeAsync,
    resetState,
  };
};
