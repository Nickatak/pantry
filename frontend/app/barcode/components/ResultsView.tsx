/**
 * Results view component - displays detected barcode and allows item creation
 *
 * Layout:
 * - Confirm Barcode section always visible below camera
 * - Edit Item form appears in a modal overlay when user confirms barcode
 */

'use client';

import { useEffect, useState } from 'react';
import { lookupProductByUPC, createItem, addItemToUser } from '../../lib/api/barcode';
import { getLocations, type Location } from '../../lib/api/locations';

interface ResultsViewProps {
  barcodeCode: string;
  onScanAnother: () => void;
}

type WorkflowStep = 'confirm-upc' | 'edit-item';

export const ResultsView = ({
  barcodeCode,
  onScanAnother,
}: ResultsViewProps) => {
  const [step, setStep] = useState<WorkflowStep>('confirm-upc');
  const [upc, setUpc] = useState(barcodeCode);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [productFound, setProductFound] = useState(false);
  const [saving, setSaving] = useState(false);
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocationId, setSelectedLocationId] = useState<number | ''>('');

  // Form state for item creation
  const [itemData, setItemData] = useState({
    barcode: barcodeCode,
    title: '',
    description: '',
    alias: '',
  });

  useEffect(() => {
    const fetchLocations = async () => {
      try {
        const data = await getLocations();
        setLocations(data);
        const pantry = data.find((location) => location.name === 'Pantry');
        if (pantry) {
          setSelectedLocationId(pantry.id);
        } else if (data.length > 0) {
          setSelectedLocationId(data[0].id);
        }
      } catch (err) {
        console.error('Failed to load locations', err);
      }
    };

    fetchLocations();
  }, []);

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
        setItemData({
          barcode: upc,
          title: (result.product_data.title as string) || '',
          description: (result.product_data.description as string) || '',
          alias: '',
        });
        setProductFound(true);
      } else {
        // Product not found in external database - allow user to manually enter data
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

    setSaving(true);
    setError(null);

    try {
      // Send item data to backend to create/save in database
      const createdItem = await createItem(itemData);
      await addItemToUser(
        createdItem.id,
        selectedLocationId === '' ? undefined : selectedLocationId
      );
      // Show success message
      setSuccess(true);
      // Wait 2 seconds to show confirmation, then reset scanner
      setTimeout(() => {
        setStep('confirm-upc');
        setSuccess(false);
        setSaving(false);
        onScanAnother();
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create item');
      setSaving(false);
    }
  };

  return (
    <>
      {/* Confirm Barcode Section - Always Visible */}
      <div className="space-y-4">
        {/* UPC Input Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-blue-900 mb-4">Scan or Enter Barcode</h2>
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

      {/* Edit Item Form */}
      {step === 'edit-item' && (
        <div className="bg-white rounded-lg shadow space-y-4">
          {/* Item Form Section */}
          <div className={`border rounded-lg p-4 ${productFound ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
            <h2 className={`text-lg font-semibold mb-4 ${productFound ? 'text-green-900' : 'text-yellow-900'}`}>
              {productFound ? 'Edit Item' : 'Add New Item'}
            </h2>

            {!productFound && (
              <div className="mb-4 p-3 bg-yellow-100 border border-yellow-300 rounded text-sm text-yellow-800">
                Product not found in database. Please enter the product information manually to add it.
              </div>
            )}

            {/* Show success message instead of form if saving succeeded */}
            {success ? (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm text-green-700 font-medium">✓ Item saved successfully! Preparing to scan next barcode...</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Barcode Field */}
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    Barcode / UPC <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={itemData.barcode}
                    disabled
                    className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-100 text-gray-500 cursor-not-allowed font-mono"
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
                    disabled={saving}
                    className={`mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none text-black disabled:bg-gray-100 disabled:text-gray-500 ${
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
                    disabled={saving}
                    className={`mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none resize-none text-black disabled:bg-gray-100 disabled:text-gray-500 ${
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
                    disabled={saving}
                    className={`mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none text-black disabled:bg-gray-100 disabled:text-gray-500 ${
                      productFound
                        ? 'focus:ring-green-500 focus:border-green-500'
                        : 'focus:ring-yellow-500 focus:border-yellow-500'
                    }`}
                    placeholder="Alternative name"
                  />
                </div>

                {/* Location Field */}
                <div>
                  <label className="text-sm font-medium text-gray-600">
                    Location
                  </label>
                  <select
                    value={selectedLocationId}
                    onChange={(e) =>
                      setSelectedLocationId(
                        e.target.value ? Number(e.target.value) : ''
                      )
                    }
                    disabled={saving || locations.length === 0}
                    className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none text-black disabled:bg-gray-100 disabled:text-gray-500"
                  >
                    <option value="">
                      {locations.length === 0
                        ? 'Loading locations...'
                        : 'Select a location'}
                    </option>
                    {locations.map((location) => (
                      <option key={location.id} value={location.id}>
                        {location.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Action Buttons - Hidden when success */}
            {!success && (
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={handleSaveItem}
                  disabled={saving}
                  className={`text-white font-medium py-2 px-4 rounded-lg transition disabled:bg-gray-400 flex items-center justify-center gap-2 ${
                    productFound
                      ? 'bg-green-600 hover:bg-green-700'
                      : 'bg-yellow-600 hover:bg-yellow-700'
                  }`}
                >
                  {saving && (
                    <div className="inline-block animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                  )}
                  {saving ? 'Saving...' : 'Save Item'}
                </button>
                <button
                  onClick={() => setStep('confirm-upc')}
                  disabled={saving}
                  className="bg-gray-200 hover:bg-gray-300 disabled:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition"
                >
                  Close
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};
