'use client';

import { Item } from '../lib/api';

// Category display names
const CATEGORY_LABELS: Record<string, string> = {
  produce: '🥬 Produce',
  dairy: '🧈 Dairy',
  meat: '🥩 Meat',
  bakery: '🍞 Bakery',
  canned: '🥫 Canned',
  frozen: '🧊 Frozen',
  pantry: '📦 Pantry',
  beverages: '🥤 Beverages',
  snacks: '🍿 Snacks',
  condiments: '🍯 Condiments',
  other: '📌 Other',
};

export function ItemCard({
  item,
  isExpanded,
  onToggleExpand,
  onEdit,
  onDelete,
  onQuickUpdateQuantity,
  isDeleting = false,
  isUpdating = false,
}: {
  item: Item;
  isExpanded: boolean;
  onToggleExpand: () => void;
  onEdit: () => void;
  onDelete: () => void;
  onQuickUpdateQuantity?: (quantity: number) => void;
  isDeleting?: boolean;
  isUpdating?: boolean;
}) {
  const categoryLabel = CATEGORY_LABELS[item.category] || CATEGORY_LABELS.other;
  const quantityValue = typeof item.quantity === 'number' ? item.quantity : 1;

  const handleQuantityChange = (nextValue: number) => {
    const normalized = Number.isFinite(nextValue) ? Math.max(1, Math.floor(nextValue)) : 1;
    if (normalized === quantityValue) return;
    onQuickUpdateQuantity?.(normalized);
  };

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden transition-all hover:border-slate-600 flex flex-col h-full">
      {/* Compact Header - Always Visible */}
      <div
        className="p-3 cursor-pointer hover:bg-slate-700/50 transition-colors flex-1"
        onClick={onToggleExpand}
      >
        <div className="space-y-2">
          {/* Title - Large and readable */}
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-base font-bold text-white line-clamp-2">
              {item.title}
            </h3>
            {typeof item.quantity === 'number' && (
              <span className="shrink-0 inline-flex items-center justify-center px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-900/60 text-emerald-200 border border-emerald-700">
                x{item.quantity}
              </span>
            )}
          </div>

          {/* Alias and Category badges */}
          <div className="flex flex-wrap gap-2">
            {item.alias && (
              <span className="inline-block text-xs bg-slate-600 text-slate-200 px-2 py-0.5 rounded whitespace-nowrap">
                {item.alias}
              </span>
            )}
            <span className="inline-block text-xs bg-blue-900 text-blue-200 px-2 py-0.5 rounded whitespace-nowrap">
              {categoryLabel}
            </span>
          </div>

          {/* Barcode - Small and condensed */}
          <div className="text-xs text-slate-400 overflow-hidden">
            <code className="bg-slate-700/50 px-1.5 py-0.5 rounded break-all">
              {item.barcode}
            </code>
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="border-t border-slate-700 p-3 bg-slate-700/20 space-y-3">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Quantity
            </label>
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => handleQuantityChange(quantityValue - 1)}
                disabled={isUpdating || quantityValue <= 1}
                className="px-2.5 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-700/50 text-white text-sm font-semibold rounded-lg transition-colors"
                aria-label="Decrease quantity"
              >
                -
              </button>
              <input
                type="number"
                min={1}
                value={quantityValue}
                onChange={(e) => handleQuantityChange(Number(e.target.value))}
                disabled={isUpdating}
                className="w-16 px-2 py-2 bg-slate-700 text-white text-sm text-center border border-slate-600 rounded-lg focus:outline-none focus:border-blue-500 disabled:opacity-60"
              />
              <button
                type="button"
                onClick={() => handleQuantityChange(quantityValue + 1)}
                disabled={isUpdating}
                className="px-2.5 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-700/50 text-white text-sm font-semibold rounded-lg transition-colors"
                aria-label="Increase quantity"
              >
                +
              </button>
            </div>
          </div>

          {item.description && (
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Description
              </label>
              <p className="text-sm text-slate-200 line-clamp-3">
                {item.description}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={onEdit}
              className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded transition-colors flex items-center justify-center gap-1"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
              Edit
            </button>
            <button
              onClick={onDelete}
              disabled={isDeleting}
              className="px-3 py-2 bg-red-600 hover:bg-red-700 disabled:bg-red-600/50 text-white text-sm font-medium rounded transition-colors flex items-center justify-center gap-1"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
