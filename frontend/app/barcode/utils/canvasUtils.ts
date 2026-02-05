/**
 * Canvas utility functions for barcode detection and visualization
 */

/**
 * Captures the current video frame and converts it to base64 JPEG
 *
 * @param videoElement - Source video element
 * @param canvasElement - Canvas to draw frame to
 * @returns Base64 encoded JPEG string (without data URL prefix)
 */
export const captureVideoFrame = (
  videoElement: HTMLVideoElement,
  canvasElement: HTMLCanvasElement
): string => {
  const context = canvasElement.getContext('2d');
  if (!context) {
    throw new Error('Could not get canvas context');
  }

  canvasElement.width = videoElement.videoWidth;
  canvasElement.height = videoElement.videoHeight;
  context.drawImage(videoElement, 0, 0);

  return canvasElement.toDataURL('image/jpeg').split(',')[1];
};

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

/**
 * Draws animated bounding box around detected barcode.
 * Includes pulsing animation and corner markers.
 *
 * @param canvas - Canvas to draw on
 * @param video - Video element (for dimensions)
 * @param box - Bounding box coordinates and size
 */
export const drawBoundingBox = (
  canvas: HTMLCanvasElement,
  video: HTMLVideoElement,
  box: BoundingBox
) => {
  // Make sure canvas matches video dimensions
  if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
  }

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw bounding box with animation effect
  ctx.strokeStyle = '#10b981';
  ctx.lineWidth = 4;
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';

  // Add pulsing effect
  const pulse = Math.sin(Date.now() / 200) * 0.3 + 0.7;
  ctx.globalAlpha = pulse;

  const { x, y, width, height } = box;

  ctx.strokeRect(x, y, width, height);

  // Add corner markers
  ctx.globalAlpha = 1;
  ctx.fillStyle = '#10b981';
  const cornerSize = 20;

  // Top-left
  ctx.fillRect(x, y, cornerSize, 3);
  ctx.fillRect(x, y, 3, cornerSize);
  // Top-right
  ctx.fillRect(x + width - cornerSize, y, cornerSize, 3);
  ctx.fillRect(x + width - 3, y, 3, cornerSize);
  // Bottom-left
  ctx.fillRect(x, y + height - 3, cornerSize, 3);
  ctx.fillRect(x, y + height - cornerSize, 3, cornerSize);
  // Bottom-right
  ctx.fillRect(x + width - cornerSize, y + height - 3, cornerSize, 3);
  ctx.fillRect(x + width - 3, y + height - cornerSize, 3, cornerSize);
};
