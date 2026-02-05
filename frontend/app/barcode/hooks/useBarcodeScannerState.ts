/**
 * Hook for managing barcode scanner state and processing
 */

import { useRef, useState } from 'react';
import { processBarcodeImage } from '../../lib/api/barcode';

/**
 * Manages barcode detection state and API processing
 *
 * FLOW:
 * - Tracks detected barcode code, loading state, and last processed time
 * - Provides throttled processing to prevent multiple rapid requests
 * - Handles both manual capture and automatic detection
 */
export const useBarcodeScannerState = () => {
  const [barcodeCode, setBarcodeCode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const lastProcessedTimeRef = useRef<number>(0);

  /**
   * Sends manually captured video frame to backend for barcode processing.
   *
   * FLOW:
   * 1. Throttles to prevent multiple requests (2s cooldown)
   * 2. Captures current video frame as JPEG
   * 3. Sends to backend API for barcode detection
   * 4. Returns result with detected status and barcode code
   * 5. Api call errors are rethrown for caller to handle
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

      const context = canvasElement.getContext('2d');
      if (!context) throw new Error('Could not get canvas context');

      canvasElement.width = videoElement.videoWidth;
      canvasElement.height = videoElement.videoHeight;
      context.drawImage(videoElement, 0, 0);

      // Convert canvas to base64
      const imageData = canvasElement
        .toDataURL('image/jpeg')
        .split(',')[1];

      // Send to backend for processing
      const result = await processBarcodeImage(imageData);

      if (result.detected && result.barcode_code) {
        setBarcodeCode(result.barcode_code);
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

  const resetState = () => {
    setBarcodeCode(null);
    setProcessing(false);
    lastProcessedTimeRef.current = 0;
  };

  return {
    barcodeCode,
    setBarcodeCode,
    loading,
    setLoading,
    processing,
    setProcessing,
    processDetectedBarcodeAsync,
    resetState,
  };
};
