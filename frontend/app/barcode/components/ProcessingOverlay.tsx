/**
 * Processing overlay component - displays feedback while server processes barcode image
 */

interface ProcessingOverlayProps {
  isVisible: boolean;
}

export const ProcessingOverlay = ({ isVisible }: ProcessingOverlayProps) => {
  if (!isVisible) return null;

  return (
    <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-40 rounded-lg z-30">
      <div className="text-center">
        {/* Spinner */}
        <div className="inline-block animate-spin rounded-full h-10 w-10 border-3 border-white border-t-blue-300 mb-3"></div>
        {/* Status message */}
        <p className="text-white font-medium text-sm">Processing...</p>
      </div>
    </div>
  );
};
