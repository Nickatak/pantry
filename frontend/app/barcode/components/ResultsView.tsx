/**
 * Results view component - displays detected barcode
 */

interface ResultsViewProps {
  barcodeCode: string;
  onScanAnother: () => void;
  onBackToDashboard: () => void;
}

export const ResultsView = ({
  barcodeCode,
  onScanAnother,
  onBackToDashboard,
}: ResultsViewProps) => {
  return (
    <div className="space-y-4">
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h2 className="text-lg font-semibold text-green-900">Barcode Found</h2>
        <p className="mt-2 text-gray-700">
          <span className="font-mono text-2xl font-bold text-green-600">
            {barcodeCode}
          </span>
        </p>
        {/* TODO: Display UPC lookup results here (product name, brand, etc.) */}
      </div>

      <button
        onClick={onScanAnother}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition"
      >
        Scan Another Barcode
      </button>

      <button
        onClick={onBackToDashboard}
        className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition"
      >
        Back to Dashboard
      </button>
    </div>
  );
};
