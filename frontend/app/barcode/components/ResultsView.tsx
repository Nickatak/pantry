/**
 * Results view component - displays detected barcode and allows item creation
 *
 * Two-step workflow:
 * 1. Confirm Barcode: Shows editable UPC field. User confirms to proceed to item creation.
 * 2. Create Item:
 *    - If product found in external database: pre-fills form with product data (green form)
 *    - If product not found: allows manual entry of all fields (yellow form with warning message)
 *    - User can edit any field and save to create the item in the database
 */

'use client';

import { useState } from 'react';
import { lookupProductByUPC, createItem } from '../../lib/api/barcode';

interface ResultsViewProps {
  barcodeCode: string;
  onScanAnother: () => void;
  onBackToDashboard: () => void;
}

type WorkflowStep = 'confirm-upc' | 'edit-item';

export const ResultsView = ({
  barcodeCode,
  onScanAnother,
  onBackToDashboard,
}: ResultsViewProps) => {
  const [step, setStep] = useState<WorkflowStep>('confirm-upc');
  const [upc, setUpc] = useState(barcodeCode);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [productFound, setProductFound] = useState(false);

  // Form state for item creation
  const [itemData, setItemData] = useState({
    barcode: barcodeCode,
    title: '',
    description: '',
    alias: '',
  });
  const [productData, setProductData] = useState<Record<string, unknown> | null>(null);

  const handleConfirmUPC = async () => {
    // Validate UPC
    if (!upc.trim()) {
      setError('UPC cannot be empty');
      return;
    }

    setLoading(true);
    setError(null);
    setProductFound(false);

    try {
      // Attempt to fetch product data from external UPC database
      const result = await lookupProductByUPC(upc);

      if (result.found && result.product_data) {
        // Successfully found - pre-fill form with external data
        setProductData(result.product_data);
        setItemData({
          barcode: upc,
          title: (result.product_data.title as string) || '',
          description: (result.product_data.description as string) || '',
          alias: '',
        });
        setProductFound(true);
      } else {
        // Product not found in external database - allow user to manually enter data
        setProductData(null);
        setItemData({
          barcode: upc,
          title: '',
          description: '',
          alias: '',
        });
        setProductFound(false);
      }

      setStep('edit-item');
    } catch (err) {
      // Backend error or network error
      const errorMessage = err instanceof Error ? err.message : 'Failed to lookup product';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveItem = async () => {
    // Validate required fields
    if (!itemData.barcode.trim()) {
      setError('Barcode is required');
      return;
    }
    if (!itemData.title.trim()) {
      setError('Title is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Send item data to backend to create/save in database
      await createItem(itemData);
      // After successful creation, reset scanner and allow another scan
      onScanAnother();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create item');
    } finally {
      setLoading(false);
    }
  };

  // Step 1: Confirm UPC
  if (step === 'confirm-upc') {
    return (
      <div className="space-y-4">
        {/* UPC Input Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-blue-900 mb-4">Confirm Barcode</h2>
          <div>
            <label className="text-sm font-medium text-gray-600">
              Barcode / UPC
            </label>
            <input
              type="text"
              value={upc}
              onChange={(e) => setUpc(e.target.value)}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-lg text-black"
              placeholder="Enter barcode"
            />
            <p className="mt-2 text-xs text-gray-500">
              Edit the barcode if needed, then click "Confirm" to proceed
            </p>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Action Buttons */}
        <button
          onClick={handleConfirmUPC}
          disabled={loading}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
        >
          {loading ? 'Loading...' : 'Confirm'}
        </button>
      </div>
    );
  }

  // Step 2: Edit Item Details
  return (
    <div className="space-y-4">
      {/* Item Form Section */}
      <div className={`border rounded-lg p-4 ${productFound ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
        <h2 className={`text-lg font-semibold mb-4 ${productFound ? 'text-green-900' : 'text-yellow-900'}`}>
          {productFound ? 'Create Item' : 'Add New Item'}
        </h2>

        {!productFound && (
          <div className="mb-4 p-3 bg-yellow-100 border border-yellow-300 rounded text-sm text-yellow-800">
            Product not found in database. Please enter the product information manually to add it.
          </div>
        )}

        <div className="space-y-4">
          {/* Barcode Field */}
          <div>
            <label className="text-sm font-medium text-gray-600">
              Barcode / UPC <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={itemData.barcode}
              onChange={(e) => setItemData({ ...itemData, barcode: e.target.value })}
              className={`mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none font-mono text-black ${
                productFound
                  ? 'focus:ring-green-500 focus:border-green-500'
                  : 'focus:ring-yellow-500 focus:border-yellow-500'
              }`}
              placeholder="Barcode"
            />
          </div>

          {/* Title Field */}
          <div>
            <label className="text-sm font-medium text-gray-600">
              Title / Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={itemData.title}
              onChange={(e) => setItemData({ ...itemData, title: e.target.value })}
              className={`mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none text-black ${
                productFound
                  ? 'focus:ring-green-500 focus:border-green-500'
                  : 'focus:ring-yellow-500 focus:border-yellow-500'
              }`}
              placeholder="Product name"
            />
          </div>

          {/* Description Field */}
          <div>
            <label className="text-sm font-medium text-gray-600">
              Description
            </label>
            <textarea
              value={itemData.description}
              onChange={(e) => setItemData({ ...itemData, description: e.target.value })}
              className={`mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none resize-none text-black ${
                productFound
                  ? 'focus:ring-green-500 focus:border-green-500'
                  : 'focus:ring-yellow-500 focus:border-yellow-500'
              }`}
              rows={3}
              placeholder="Product description"
            />
          </div>

          {/* Alias Field */}
          <div>
            <label className="text-sm font-medium text-gray-600">
              Alias / Alternative Name
            </label>
            <input
              type="text"
              value={itemData.alias}
              onChange={(e) => setItemData({ ...itemData, alias: e.target.value })}
              className={`mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none text-black ${
                productFound
                  ? 'focus:ring-green-500 focus:border-green-500'
                  : 'focus:ring-yellow-500 focus:border-yellow-500'
              }`}
              placeholder="Alternative name"
            />
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Product Data Preview */}
      {productData && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <p className="text-sm font-medium text-gray-600 mb-2">External Product Data</p>
          <div className="text-xs text-gray-600 space-y-1">
            {productData.brand && <p><strong>Brand:</strong> {String(productData.brand)}</p>}
            {productData.category && <p><strong>Category:</strong> {String(productData.category)}</p>}
            {productData.size && <p><strong>Size:</strong> {String(productData.size)}</p>}
            {productData.quantity && <p><strong>Quantity:</strong> {String(productData.quantity)}</p>}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={handleSaveItem}
          disabled={loading}
          className={`text-white font-medium py-2 px-4 rounded-lg transition disabled:bg-gray-400 ${
            productFound
              ? 'bg-green-600 hover:bg-green-700'
              : 'bg-yellow-600 hover:bg-yellow-700'
          }`}
        >
          {loading ? 'Saving...' : 'Save Item'}
        </button>
        <button
          onClick={() => setStep('confirm-upc')}
          disabled={loading}
          className="bg-gray-200 hover:bg-gray-300 disabled:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded-lg transition"
        >
          Back
        </button>
      </div>

      <button
        onClick={onScanAnother}
        disabled={loading}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
      >
        Scan Another Barcode
      </button>

      <button
        onClick={onBackToDashboard}
        disabled={loading}
        className="w-full bg-gray-200 hover:bg-gray-300 disabled:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded-lg transition"
      >
        Back to Dashboard
      </button>
    </div>
  );
};
