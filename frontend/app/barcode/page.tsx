'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCamera } from './hooks/useCamera';
import { useDetectionFeedback } from './hooks/useDetectionFeedback';
import { useHtml5Scanner } from './hooks/useHtml5Scanner';
import { useBarcodeScannerState } from './hooks/useBarcodeScannerState';
import { useManualBarcodeCapture } from './hooks/useManualBarcodeCapture';
import { ErrorDisplay } from './components/ErrorDisplay';
import { CameraView } from './components/CameraView';
import { ResultsView } from './components/ResultsView';
import { html5QrcodeScannerStyles } from './styles';

// Add fade-out animation for flash effect
const flashAnimationStyle = `
  @keyframes fadeOut {
    from {
      opacity: 0.4;
    }
    to {
      opacity: 0;
    }
  }
`;

/**
 * BARCODE SCANNER PAGE
 *
 * FLOW:
 * 1. User captures image with camera
 * 2. Image sent to /api/barcode/process/ - extracts barcode/UPC
 * 3. ResultsView shows extracted barcode for confirmation/editing
 * 4. User confirms barcode and fetches product data
 * 5. User edits item details and saves to database
 */

export default function BarcodePage() {
  const router = useRouter();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [cameraInitializationRequested, setCameraInitializationRequested] =
    useState(false);

  // Custom hooks for separation of concerns
  const camera = useCamera();
  const scannerState = useBarcodeScannerState();
  const detectionFeedback = useDetectionFeedback();
  const html5Scanner = useHtml5Scanner({
    onDetection: (barcode) => {
      // Just set the barcode code, don't fetch item data
      scannerState.setBarcodeCode(barcode);
      detectionFeedback.showDetectionFeedback();
    },
    onScannerReady: () => {
      camera.setCameraActive(true);
    },
    detectionMethodActive: camera.detectionMethod === 'html5qrcode' && cameraInitializationRequested,
  });

  const { captureFromBarcodeDetector, captureFromHtml5Scanner } =
    useManualBarcodeCapture({
      onProcessBarcodeAsync: async (videoElement: HTMLVideoElement, canvasElement: HTMLCanvasElement) => {
        // Just extract barcode, don't fetch item data
        return await scannerState.processDetectedBarcodeOnlyAsync(videoElement, canvasElement);
      },
      onSetProcessing: scannerState.setProcessing,
      onSetError: camera.setError,
      onShowFeedback: detectionFeedback.showDetectionFeedback,
      onStopCamera: camera.stopCamera,
    });

  // Check authentication and initialize camera on mount
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (!token) {
      router.push('/login');
      return;
    }

    // Inject styles to hide html5-qrcode dashboard and flash animation
    const styleTag = document.createElement('style');
    styleTag.innerHTML = html5QrcodeScannerStyles + flashAnimationStyle;
    document.head.appendChild(styleTag);

    return () => {
      document.head.removeChild(styleTag);
    };
  }, [router]);

  // Initialize camera only when user requests it
  useEffect(() => {
    if (cameraInitializationRequested) {
      camera.initializeCamera();
    }
  }, [cameraInitializationRequested]);

  // Handle manual capture for BarcodeDetector mode
  const handleManualCapture = async () => {
    if (!camera.videoRef.current || !canvasRef.current) return;
    await captureFromBarcodeDetector(camera.videoRef.current, canvasRef.current);
  };

  // Handle manual capture for html5-qrcode mode
  const handleManualCaptureHtml5 = async () => {
    if (!canvasRef.current) return;
    await captureFromHtml5Scanner(canvasRef.current, html5Scanner.html5ScannerRef.current);
  };

  // Handle retry/reset
  const handleRetry = () => {
    scannerState.resetState();
    detectionFeedback.setBarcodeDetected(false);
    camera.setError(null);

    if (
      html5Scanner.html5ScannerRef.current &&
      camera.detectionMethod === 'html5qrcode'
    ) {
      try {
        html5Scanner.clearScanner().then(() => {
          setTimeout(() => {
            html5Scanner.initializeHtml5Scanner();
          }, 100);
        });
      } catch (err) {
        console.log('Error clearing scanner, reinitializing camera...', err);
        html5Scanner.html5ScannerRef.current = null;
        camera.initializeCamera();
      }
    } else {
      camera.initializeCamera();
    }
  };



  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">Barcode Scanner</h1>
            <p className="mt-1 text-sm text-gray-600">
              Point your camera at a barcode to scan it
            </p>
          </div>

          <div className="p-6 space-y-6">
            <ErrorDisplay error={camera.error} />

            <CameraView
              cameraInitializationRequested={cameraInitializationRequested}
              onRequestCameraInitialization={() =>
                setCameraInitializationRequested(true)
              }
              detectionMethod={camera.detectionMethod}
              cameraActive={camera.cameraActive}
              videoRef={camera.videoRef}
              barcodeDetected={detectionFeedback.barcodeDetected}
              loading={scannerState.loading}
              processing={scannerState.processing}
              onManualCapture={
                camera.detectionMethod === 'html5qrcode'
                  ? handleManualCaptureHtml5
                  : handleManualCapture
              }
            />

            <ResultsView
              barcodeCode={scannerState.barcodeCode || ''}
              onScanAnother={handleRetry}
            />

            <canvas ref={canvasRef} className="hidden" />
          </div>
        </div>
      </div>
    </div>
  );
}
