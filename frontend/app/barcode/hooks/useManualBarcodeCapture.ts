/**
 * Hook for managing barcode manual capture logic
 * Handles both BarcodeDetector and html5-qrcode capture modes
 */

import { useRef, useCallback } from 'react';

interface UseManualBarcodeCapture {
  onProcessBarcodeAsync: (
    videoElement: HTMLVideoElement,
    canvasElement: HTMLCanvasElement
  ) => Promise<boolean>;
  onSetProcessing: (state: boolean) => void;
  onSetError: (error: string | null) => void;
  onShowFeedback: () => void;
  onStopCamera: () => void;
}

/**
 * Unified manual capture handler that works for both detection methods
 *
 * FLOW:
 * 1. Gets video element based on detection method
 * 2. Processes the frame through the backend API
 * 3. Shows feedback or error
 * 4. Handles scanner cleanup (html5-qrcode only)
 */
export const useManualBarcodeCapture = ({
  onProcessBarcodeAsync,
  onSetProcessing,
  onSetError,
  onShowFeedback,
  onStopCamera,
}: UseManualBarcodeCapture) => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const html5ScannerRef = useRef<any>(null);

  const captureBarcode = useCallback(
    async (
      videoElement: HTMLVideoElement,
      canvasElement: HTMLCanvasElement,
      options?: { pauseHtml5Scanner?: boolean }
    ) => {
      try {
        onSetProcessing(true);
        onSetError(null);

        if (!videoElement) throw new Error('Video element not found');
        if (!canvasElement) throw new Error('Canvas not found');

        const result = await onProcessBarcodeAsync(videoElement, canvasElement);

        if (result) {
          onShowFeedback();
          onStopCamera();

          // Pause html5-qrcode scanner if applicable
          if (options?.pauseHtml5Scanner && html5ScannerRef.current) {
            await html5ScannerRef.current.pause();
          }
        } else {
          onSetError('Could not read the barcode. Please try again.');
        }
      } catch (err) {
        console.error('Error capturing barcode:', err);
        onSetError(
          `Failed to capture barcode: ${
            err instanceof Error ? err.message : 'Unknown error'
          }`
        );
      } finally {
        onSetProcessing(false);
      }
    },
    [
      onProcessBarcodeAsync,
      onSetProcessing,
      onSetError,
      onShowFeedback,
      onStopCamera,
    ]
  );

  const captureFromBarcodeDetector = useCallback(
    async (videoElement: HTMLVideoElement, canvasElement: HTMLCanvasElement) => {
      return captureBarcode(videoElement, canvasElement);
    },
    [captureBarcode]
  );

  const captureFromHtml5Scanner = useCallback(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    async (canvasElement: HTMLCanvasElement, scanner: any) => {
      const container = document.getElementById('barcode-scanner-container');
      if (!container) throw new Error('Scanner container not found');

      const videoElement = container.querySelector('video');
      if (!videoElement) throw new Error('Video element not found in scanner');

      html5ScannerRef.current = scanner;
      return captureBarcode(videoElement, canvasElement, {
        pauseHtml5Scanner: true,
      });
    },
    [captureBarcode]
  );

  return {
    captureFromBarcodeDetector,
    captureFromHtml5Scanner,
  };
};
