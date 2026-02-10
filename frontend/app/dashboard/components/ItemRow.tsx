'use client';

import { Item } from '../lib/api';

const CATEGORIES = [
  { value: 'produce', label: '🥬 Produce' },
  { value: 'dairy', label: '🧈 Dairy' },
  { value: 'meat', label: '🥩 Meat & Poultry' },
  { value: 'bakery', label: '🍞 Bakery' },
  { value: 'canned', label: '🥫 Canned' },
  { value: 'frozen', label: '🧊 Frozen' },
  { value: 'pantry', label: '📦 Pantry' },
  { value: 'beverages', label: '🥤 Beverages' },
  { value: 'snacks', label: '🍿 Snacks' },
  { value: 'condiments', label: '🍯 Condiments' },
  { value: 'other', label: '📌 Other' },
];

export function ItemRow({
  item,
  onEdit,
  onDelete,
  onQuickUpdateCategory,
  onQuickUpdateQuantity,
  isDeleting = false,
  isUpdating = false,
}: {
  item: Item;
  onEdit: () => void;
  onDelete: () => void;
  onQuickUpdateCategory: (category: string) => void;
  onQuickUpdateQuantity: (quantity: number) => void;
  isDeleting?: boolean;
  isUpdating?: boolean;
}) {
  const quantityValue = typeof item.quantity === 'number' ? item.quantity : 1;

  const handleQuantityChange = (nextValue: number) => {
    const normalized = Number.isFinite(nextValue) ? Math.max(1, Math.floor(nextValue)) : 1;
    if (normalized === quantityValue) return;
    onQuickUpdateQuantity(normalized);
  };

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 p-3 flex flex-col sm:flex-row sm:items-center gap-3">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 text-white font-semibold text-sm sm:text-base truncate">
          <span className="truncate">{item.title}</span>
          {typeof item.quantity === 'number' && (
            <span className="inline-flex items-center justify-center px-2 py-0.5 text-xs sm:text-sm font-semibold rounded-full bg-emerald-900/60 text-emerald-200 border border-emerald-700">
              x{item.quantity}
            </span>
          )}
        </div>
        <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
          {item.alias && (
            <span className="bg-slate-700 px-2 py-0.5 rounded">
              {item.alias}
            </span>
          )}
          <code className="bg-slate-700/50 px-2 py-0.5 rounded break-all">
            {item.barcode}
          </code>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => handleQuantityChange(quantityValue - 1)}
            disabled={isUpdating || quantityValue <= 1}
            className="px-2.5 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-700/50 text-white text-sm sm:text-base font-semibold rounded-lg transition-colors"
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
            className="w-16 px-2 py-2 bg-slate-700 text-white text-sm sm:text-base text-center border border-slate-600 rounded-lg focus:outline-none focus:border-blue-500 disabled:opacity-60"
          />
          <button
            type="button"
            onClick={() => handleQuantityChange(quantityValue + 1)}
            disabled={isUpdating}
            className="px-2.5 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-700/50 text-white text-sm sm:text-base font-semibold rounded-lg transition-colors"
            aria-label="Increase quantity"
          >
            +
          </button>
        </div>

        <select
          value={item.category || 'other'}
          onChange={(e) => onQuickUpdateCategory(e.target.value)}
          disabled={isUpdating}
          className="px-3 py-2.5 bg-slate-700 text-white text-sm sm:text-base border border-slate-600 rounded-lg focus:outline-none focus:border-blue-500 disabled:opacity-60"
        >
          {CATEGORIES.map((cat) => (
            <option key={cat.value} value={cat.value}>
              {cat.label}
            </option>
          ))}
        </select>

        <button
          onClick={onEdit}
          className="px-3 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm sm:text-base font-medium rounded transition-colors"
        >
          Edit
        </button>
        <button
          onClick={onDelete}
          disabled={isDeleting}
          className="px-3 py-2.5 bg-red-600 hover:bg-red-700 disabled:bg-red-600/50 text-white text-sm sm:text-base font-medium rounded transition-colors"
        >
          {isDeleting ? 'Deleting...' : 'Delete'}
        </button>
      </div>
    </div>
  );
}
