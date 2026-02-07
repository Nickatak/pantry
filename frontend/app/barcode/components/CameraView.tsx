/**
 * Camera view component - displays camera feed and controls
 */

import React, { useRef } from 'react';
import { DetectionMethod } from '../hooks/useCamera';

interface CameraViewProps {
  cameraInitializationRequested: boolean;
  onRequestCameraInitialization: () => void;
  detectionMethod: DetectionMethod;
  cameraActive: boolean;
  videoRef: React.RefObject<HTMLVideoElement>;
  barcodeDetected: boolean;
  loading: boolean;
  processing: boolean;
  onManualCapture: () => void;
  onCancel: () => void;
}

export const CameraView = ({
  cameraInitializationRequested,
  onRequestCameraInitialization,
  detectionMethod,
  cameraActive,
  videoRef,
  barcodeDetected,
  loading,
  processing,
  onManualCapture,
  onCancel,
}: CameraViewProps) => {
  const canvasOverlayRef = useRef<HTMLCanvasElement>(null);

  // Show initialization prompt if camera hasn't been requested yet
  if (!cameraInitializationRequested) {
    return (
      <div className="space-y-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <h2 className="text-lg font-semibold text-blue-900 mb-2">Ready to Scan?</h2>
          <p className="text-blue-700 mb-4">
            Click below to enable your camera and start scanning barcodes
          </p>
          <button
            onClick={onRequestCameraInitialization}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg transition"
          >
            Enable Camera
          </button>
        </div>
        <button
          onClick={onCancel}
          className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition"
        >
          Cancel
        </button>
      </div>
    );
  }

  // Show camera feed once initialized
  return (
    <div className="space-y-4">
      {detectionMethod === 'html5qrcode' ? (
        // html5-qrcode scanner container
        <div className="relative rounded-lg overflow-hidden bg-black w-full" style={{ minHeight: '400px' }}>
          <div
            id="barcode-scanner-container"
            className="w-full h-full"
          />
          {!cameraActive && cameraInitializationRequested && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-75 z-10">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-600 border-t-white mb-4"></div>
                <p className="text-white font-medium">Initializing camera...</p>
              </div>
            </div>
          )}
        </div>
      ) : (
        // Video element for BarcodeDetector
        <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full h-full object-cover"
          />
          <canvas
            ref={canvasOverlayRef}
            className="absolute inset-0 w-full h-full hidden"
          />
          {!cameraActive && cameraInitializationRequested && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-75 z-10">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-600 border-t-white mb-4"></div>
                <p className="text-white font-medium">Initializing camera...</p>
              </div>
            </div>
          )}
          {cameraActive && (
            <div className="absolute inset-0 border-4 border-green-400 opacity-50"></div>
          )}
          {barcodeDetected && (
            <div className="absolute inset-0 bg-green-500 opacity-10"></div>
          )}
        </div>
      )}

      {barcodeDetected && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <p className="text-green-800 font-semibold text-center">
            ✓ Barcode Read Successfully!
          </p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={onManualCapture}
          disabled={!cameraActive || loading || processing}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
        >
          {loading || processing ? 'Processing...' : 'Capture'}
        </button>

        <button
          onClick={onCancel}
          className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};
