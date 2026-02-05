/**
 * Hook for managing barcode detection visual and audio feedback
 */

import { useEffect, useRef, useState } from 'react';
import { playDetectionSound } from '../utils/audioUtils';

/**
 * Manages detection feedback (green flash + sound)
 *
 * FLOW:
 * 1. Sets barcodeDetected to true
 * 2. Plays detection sound
 * 3. Auto-resets after 500ms
 */
export const useDetectionFeedback = () => {
  const [barcodeDetected, setBarcodeDetected] = useState(false);
  const detectionFlashRef = useRef<NodeJS.Timeout | null>(null);

  const showDetectionFeedback = () => {
    // Show visual feedback
    setBarcodeDetected(true);
    playDetectionSound();

    // Clear any existing timeout
    if (detectionFlashRef.current) {
      clearTimeout(detectionFlashRef.current);
    }

    // Reset feedback after 500ms
    detectionFlashRef.current = setTimeout(() => {
      setBarcodeDetected(false);
    }, 500);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (detectionFlashRef.current) {
        clearTimeout(detectionFlashRef.current);
      }
    };
  }, []);

  return {
    barcodeDetected,
    setBarcodeDetected,
    showDetectionFeedback,
    detectionFlashRef,
  };
};
