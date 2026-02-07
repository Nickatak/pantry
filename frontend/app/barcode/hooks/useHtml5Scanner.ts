/**
 * Hook for managing html5-qrcode scanner lifecycle
 */

import { useEffect, useRef } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';

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
  const html5ScannerRef = useRef<InstanceType<typeof Html5QrcodeScanner> | null>(
    null
  );

  const initializeHtml5Scanner = async () => {
    try {
      // Check if container exists
      const container = document.getElementById('barcode-scanner-container');
      if (!container) {
        console.error('Container not found: barcode-scanner-container');
        throw new Error('Scanner container not found in DOM');
      }

      console.log('Container found, initializing html5-qrcode scanner...');

      // Get the actual aspect ratio from the camera
      let aspectRatio = 1.77778; // Default fallback
      try {

        // Try to get aspect ratio from the actual video stream by checking container dimensions
        // as a fallback, we'll let the video element determine it naturally
        const containerWidth = container.offsetWidth;
        const containerHeight = container.offsetHeight;

        if (containerWidth && containerHeight) {
          aspectRatio = containerWidth / containerHeight;
          console.log('Camera aspect ratio calculated:', aspectRatio);
        }
      } catch (e) {
        console.log('Could not determine camera aspect ratio, using default:', e);
      }

      const scanner = new Html5QrcodeScanner(
        'barcode-scanner-container',
        {
          fps: 30,
          qrbox: { width: 250, height: 250 },
          aspectRatio: aspectRatio,
          disableFlip: false,
          showTorchButtonIfSupported: true,
          showZoomedQrImage: false,
        },
        false
      );

      html5ScannerRef.current = scanner;

      scanner.render(
        async (decodedText) => {
          // Barcode detected
          console.log('Barcode detected via html5-qrcode:', decodedText);
          onDetection(decodedText);

          // Pause the scanner to stop immediate re-detection
          if (html5ScannerRef.current) {
            try {
              await html5ScannerRef.current.pause();
              console.log('Scanner paused, ready for user action');
            } catch (e) {
              console.log('Error pausing scanner:', e);
            }
          }
        },
        (errorMessage) => {
          // Not a critical error, just logging failed attempts
          console.debug('html5-qrcode scan attempt:', errorMessage);
        }
      );

      // Wait for the video element inside the container to actually start rendering
      const checkVideoReady = () => {
        const videoElement = document.querySelector('#barcode-scanner-container video');
        if (videoElement && (videoElement as HTMLVideoElement).readyState >= 2) {
          console.log('✓ html5-qrcode video stream ready');
          onScannerReady?.();
        } else {
          setTimeout(checkVideoReady, 100);
        }
      };
      checkVideoReady();
    } catch (err) {
      console.error('Failed to initialize html5-qrcode scanner:', err);
      throw err;
    }
  };

  const clearScanner = async () => {
    if (html5ScannerRef.current) {
      try {
        await html5ScannerRef.current.clear();
        html5ScannerRef.current = null;
        console.log('Scanner cleared');
      } catch (err) {
        console.log('Could not clear scanner:', err);
      }
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

      return () => clearTimeout(timer);
    }
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
