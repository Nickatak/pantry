/**
 * Results view component - displays detected barcode and product information
 */

import { ItemData } from '../../lib/api/barcode';

interface ResultsViewProps {
  barcodeCode: string;
  itemData: ItemData | null;
  productData: Record<string, unknown> | null;
  lookupError: string | null;
  onScanAnother: () => void;
  onBackToDashboard: () => void;
}

const isNonEmptyValue = (value: unknown): boolean => {
  return value !== null && value !== undefined && value !== '';
};

export const ResultsView = ({
  barcodeCode,
  itemData,
  productData,
  lookupError,
  onScanAnother,
  onBackToDashboard,
}: ResultsViewProps) => {
  // Filter product data to only show non-empty values
  const displayableProductData = productData
    ? {
        brand: productData.brand,
        category: productData.category,
        size: productData.size,
        quantity: productData.quantity,
      }
    : null;

  return (
    <div className="space-y-4">
      {/* Barcode Detection Section */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h2 className="text-lg font-semibold text-green-900">Barcode Found</h2>
        <p className="mt-2 text-gray-700">
          <span className="font-mono text-2xl font-bold text-green-600">
            {barcodeCode}
          </span>
        </p>
      </div>

      {/* Product Information Section */}
      {itemData ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">Product Information</h3>

          <div className="space-y-3">
            {/* Product Title */}
            {itemData.title && (
              <div>
                <p className="text-sm font-medium text-gray-600">Product Name</p>
                <p className="text-gray-900">{itemData.title}</p>
              </div>
            )}

            {/* Description */}
            {itemData.description && (
              <div>
                <p className="text-sm font-medium text-gray-600">Description</p>
                <p className="text-gray-700 text-sm">{itemData.description}</p>
              </div>
            )}

            {/* UPC/Barcode */}
            <div>
              <p className="text-sm font-medium text-gray-600">UPC/Barcode</p>
              <p className="font-mono text-gray-900">{itemData.barcode}</p>
            </div>

            {/* Additional Product Data (if available) */}
            {displayableProductData && (
              <div className="border-t border-blue-200 pt-3 mt-3">
                <p className="text-sm font-medium text-gray-600 mb-2">Additional Details</p>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {isNonEmptyValue(displayableProductData.brand) && (
                    <div>
                      <p className="text-gray-600">Brand:</p>
                      <p className="text-gray-900 font-medium">{String(displayableProductData.brand)}</p>
                    </div>
                  )}
                  {isNonEmptyValue(displayableProductData.category) && (
                    <div>
                      <p className="text-gray-600">Category:</p>
                      <p className="text-gray-900 font-medium">{String(displayableProductData.category)}</p>
                    </div>
                  )}
                  {isNonEmptyValue(displayableProductData.size) && (
                    <div>
                      <p className="text-gray-600">Size:</p>
                      <p className="text-gray-900 font-medium">{String(displayableProductData.size)}</p>
                    </div>
                  )}
                  {isNonEmptyValue(displayableProductData.quantity) && (
                    <div>
                      <p className="text-gray-600">Quantity:</p>
                      <p className="text-gray-900 font-medium">{String(displayableProductData.quantity)}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      ) : lookupError ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-yellow-900">Barcode Detected</h3>
          <p className="mt-2 text-yellow-700 text-sm">
            Barcode recognized but product information could not be loaded.
          </p>
          <p className="mt-1 text-yellow-600 text-xs">{lookupError}</p>
        </div>
      ) : (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <p className="text-gray-700 text-sm">Loading product information...</p>
        </div>
      )}

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
