/**
 * Camera view component - displays camera feed and controls
 */

import React, { useRef } from 'react';
import { DetectionMethod } from '../hooks/useCamera';

interface CameraViewProps {
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

  return (
    <div className="space-y-4">
      {detectionMethod === 'html5qrcode' ? (
        // html5-qrcode scanner container
        <div
          id="barcode-scanner-container"
          className="rounded-lg overflow-hidden bg-black w-full"
          style={{ minHeight: '400px' }}
        />
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
          {!cameraActive && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
              <p className="text-white text-center">
                Requesting camera access...
              </p>
            </div>
          )}
          {cameraActive && (
            <div className="absolute inset-0 border-4 opacity-50 border-green-400"></div>
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

      {cameraActive && (
        <p className="text-sm text-gray-600 text-center">
          {detectionMethod === 'html5qrcode' ? (
            <span className="text-blue-600 font-semibold">
              ✓ Real-time barcode detection active (html5-qrcode)
            </span>
          ) : detectionMethod === 'barcodedetector' ? (
            <span className="text-blue-600 font-semibold">
              ✓ Real-time barcode detection active (Native API)
            </span>
          ) : (
            'Initializing barcode detection...'
          )}
        </p>
      )}
    </div>
  );
};
