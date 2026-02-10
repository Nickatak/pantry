/**
 * Hook for managing html5-qrcode scanner lifecycle
 */

import { useEffect, useRef } from 'react';
import { Html5Qrcode } from 'html5-qrcode';

interface UseHtml5ScannerOptions {
  onDetection: (barcode: string) => void;
  onScannerReady?: () => void;
  detectionMethodActive: boolean;
}

/**
 * Manages html5-qrcode scanner initialization and cleanup
 *
 * CALLED FROM:
 * - useEffect watching detectionMethod (when set to 'html5qrcode')
 *
 * FLOW:
 * 1. Checks if DOM container exists
 * 2. Creates Html5QrcodeScanner instance
 * 3. Attaches detection callback that pauses scanner when barcode found
 * 4. Cleans up on unmount or dependency change
 */
export const useHtml5Scanner = ({
  onDetection,
  onScannerReady,
  detectionMethodActive,
}: UseHtml5ScannerOptions) => {
  const html5ScannerRef = useRef<InstanceType<typeof Html5Qrcode> | null>(null);
  const initializingRef = useRef(false);

  const initializeHtml5Scanner = async () => {
    if (initializingRef.current || html5ScannerRef.current) {
      return;
    }
    initializingRef.current = true;
    try {
      // Check if container exists
      const container = document.getElementById('barcode-scanner-container');
      if (!container) {
        console.error('Scanner container not found in DOM');
        throw new Error('Scanner container not found in DOM');
      }

      // Get the actual aspect ratio from the camera
      let aspectRatio = 1.77778; // Default fallback
      try {

        // Try to get aspect ratio from the actual video stream by checking container dimensions
        // as a fallback, we'll let the video element determine it naturally
        const containerWidth = container.offsetWidth;
        const containerHeight = container.offsetHeight;

        if (containerWidth && containerHeight) {
          aspectRatio = containerWidth / containerHeight;
        }
      } catch (e) {
        console.error('Could not determine camera aspect ratio, using default:', e);
      }

      const scanner = new Html5Qrcode('barcode-scanner-container');

      await scanner.start(
        { facingMode: 'environment' },
        {
          fps: 30,
          qrbox: { width: 250, height: 250 },
          aspectRatio: aspectRatio,
          disableFlip: false,
        },
        (decodedText) => {
          onDetection(decodedText);
          try {
            scanner.pause(true);
          } catch (e) {
            console.error('Error pausing scanner:', e);
          }
        },
        () => {}
      );

      html5ScannerRef.current = scanner;
      onScannerReady?.();
    } catch (err) {
      console.error('Failed to initialize html5-qrcode scanner:', err);
      html5ScannerRef.current = null;
      throw err;
    } finally {
      initializingRef.current = false;
    }
  };

  const clearScanner = async () => {
    if (!html5ScannerRef.current) {
      return;
    }

    try {
      await html5ScannerRef.current.stop();
    } catch (err) {
      console.error('Could not stop scanner:', err);
    }

    try {
      html5ScannerRef.current.clear();
    } catch (err) {
      console.error('Could not clear scanner:', err);
    } finally {
      html5ScannerRef.current = null;
    }
  };

  // Initialize scanner when detection method becomes active
  useEffect(() => {
    if (detectionMethodActive) {
      // Small delay to ensure DOM is fully ready
      const timer = setTimeout(() => {
        initializeHtml5Scanner().catch((err) => {
          console.error('Failed to initialize scanner:', err);
        });
      }, 100);

      return () => {
        clearTimeout(timer);
        clearScanner();
      };
    }
    return () => {};
  }, [detectionMethodActive]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearScanner();
    };
  }, []);

  return {
    html5ScannerRef,
    initializeHtml5Scanner,
    clearScanner,
  };
};
