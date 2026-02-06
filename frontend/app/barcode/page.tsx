'use client';

import { useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useCamera } from './hooks/useCamera';
import { useDetectionFeedback } from './hooks/useDetectionFeedback';
import { useHtml5Scanner } from './hooks/useHtml5Scanner';
import { useBarcodeScannerState } from './hooks/useBarcodeScannerState';
import { useManualBarcodeCapture } from './hooks/useManualBarcodeCapture';
import { ErrorDisplay } from './components/ErrorDisplay';
import { CameraView } from './components/CameraView';
import { ResultsView } from './components/ResultsView';

/**
 * BARCODE SCANNER PAGE
 *
 * FLOW:
 * 1. User captures image with camera
 * 2. Image sent to /api/barcode/process/ - extracts barcode/UPC
 * 3. UPC sent to /api/items/{UPC} - retrieves product information
 * 4. Product details displayed in ResultsView
 */

export default function BarcodePage() {
  const router = useRouter();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Custom hooks for separation of concerns
  const camera = useCamera();
  const scannerState = useBarcodeScannerState();
  const detectionFeedback = useDetectionFeedback();
  const html5Scanner = useHtml5Scanner({
    onDetection: async (barcode) => {
      // Auto-fetch item data when barcode is detected
      try {
        await scannerState.lookupItemByBarcodeAsync(barcode);
        detectionFeedback.showDetectionFeedback();
      } catch (err) {
        console.error('Error processing auto-detected barcode:', err);
        camera.setError('Failed to process barcode');
      }
    },
    onScannerReady: () => {
      camera.setCameraActive(true);
    },
    detectionMethodActive: camera.detectionMethod === 'html5qrcode',
  });

  const { captureFromBarcodeDetector, captureFromHtml5Scanner } =
    useManualBarcodeCapture({
      onProcessBarcodeAsync: scannerState.processDetectedBarcodeAsync,
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

    camera.initializeCamera();
  }, [router]);

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

          <div className="p-6">
            {scannerState.barcodeCode ? (
              <ResultsView
                barcodeCode={scannerState.barcodeCode}
                itemData={scannerState.itemData}
                productData={scannerState.productData}
                lookupError={scannerState.lookupError}
                onScanAnother={handleRetry}
                onBackToDashboard={() => router.push('/dashboard')}
              />
            ) : (
              <>
                <ErrorDisplay error={camera.error} />

                <CameraView
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
                  onCancel={() => router.push('/dashboard')}
                />

                <canvas ref={canvasRef} className="hidden" />
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
