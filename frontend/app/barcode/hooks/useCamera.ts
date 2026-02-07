/**
 * Hook for managing camera stream initialization and lifecycle
 */

import { useEffect, useRef, useState } from 'react';

export type DetectionMethod = 'barcodedetector' | 'html5qrcode' | null;

/**
 * Camera management hook
 * Handles:
 * - Requesting camera permissions
 * - Detecting BarcodeDetector API support
 * - Setting up video stream
 * - Cleanup on unmount
 *
 * FLOW:
 * 1. Requests camera permissions from user
 * 2. Checks if BarcodeDetector API is available
 * 3. Sets detectionMethod accordingly
 * 4. Returns refs and state for caller to manage detection
 */
export const useCamera = (
  onDetectionMethodChange?: (method: DetectionMethod) => void
) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detectionMethod, setDetectionMethod] = useState<DetectionMethod>(null);

  const initializeCamera = async () => {
    try {
      console.log('Requesting camera permissions...');
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 },
          focusMode: 'continuous',
        } as MediaTrackConstraints & { focusMode: string },
      });

      console.log('✓ Camera permissions granted');

      // Check if BarcodeDetector is supported
      let isSupported = false;
      if ('BarcodeDetector' in window) {
        try {
          // Simple test - just try to instantiate
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          const barcodeDetectorClass = (window as any).BarcodeDetector;
          new barcodeDetectorClass({ formats: ['qr_code'] });
          isSupported = true;
          console.log('✓ BarcodeDetector API is supported');

          // Use BarcodeDetector with the stream
          if (videoRef.current) {
            videoRef.current.srcObject = stream;

            // Wait for the video to actually have frames before marking as active
            const handleCanPlay = () => {
              setCameraActive(true);
              videoRef.current?.removeEventListener('canplay', handleCanPlay);
            };
            videoRef.current.addEventListener('canplay', handleCanPlay);

            setDetectionMethod('barcodedetector');
            onDetectionMethodChange?.('barcodedetector');
          }
        } catch (e) {
          console.log('✗ BarcodeDetector API exists but not fully supported:', e);
          stream.getTracks().forEach((track) => track.stop());
          isSupported = false;
        }
      }

      if (!isSupported) {
        // Stop the stream - html5-qrcode will request its own
        stream.getTracks().forEach((track) => track.stop());

        // Fall back to html5-qrcode for desktop browsers
        console.log('↻ Initializing html5-qrcode for desktop barcode detection');
        setDetectionMethod('html5qrcode');
        onDetectionMethodChange?.('html5qrcode');
      }
    } catch (err) {
      const message =
        'Failed to access camera. Please ensure you have granted camera permissions.';
      setError(message);
      console.error('Camera access error:', err);
    }
  };

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
      tracks.forEach((track) => track.stop());
      setCameraActive(false);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  return {
    videoRef,
    cameraActive,
    setCameraActive,
    error,
    setError,
    detectionMethod,
    setDetectionMethod,
    initializeCamera,
    stopCamera,
  };
};
