'use client';

import { useState } from 'react';
import { Item } from '../lib/api';
import { ItemCard } from './ItemCard';
import { ItemRow } from './ItemRow';

export function ItemsList({
  items,
  onEdit,
  onDelete,
  onQuickUpdateCategory,
  onQuickUpdateQuantity,
  isLoading = false,
  isDeletingId = null,
  isUpdatingId = null,
  viewMode = 'cards',
}: {
  items: Item[];
  onEdit: (item: Item) => void;
  onDelete: (id: number) => void;
  onQuickUpdateCategory?: (id: number, category: string) => void;
  onQuickUpdateQuantity?: (id: number, quantity: number) => void;
  isLoading?: boolean;
  isDeletingId?: number | null;
  isUpdatingId?: number | null;
  viewMode?: 'compact' | 'cards';
}) {
  const [expandedId, setExpandedId] = useState<number | null>(null);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-slate-300">Loading items...</div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-8 text-center">
        <p className="text-slate-300 mb-4">No items found</p>
        <p className="text-slate-400 text-sm">
          Scan a barcode or add items manually to get started
        </p>
      </div>
    );
  }

  // Group items by category
  const groupedItems = items.reduce(
    (acc, item) => {
      const category = item.category || 'other';
      if (!acc[category]) {
        acc[category] = [];
      }
      acc[category].push(item);
      return acc;
    },
    {} as Record<string, Item[]>
  );

  const CATEGORY_LABELS: Record<string, string> = {
    produce: '🥬 Produce',
    dairy: '🧈 Dairy',
    meat: '🥩 Meat & Poultry',
    bakery: '🍞 Bakery',
    canned: '🥫 Canned Goods',
    frozen: '🧊 Frozen',
    pantry: '📦 Pantry Staples',
    beverages: '🥤 Beverages',
    snacks: '🍿 Snacks',
    condiments: '🍯 Condiments',
    other: '📌 Other',
  };

  const categoryOrder = [
    'produce',
    'dairy',
    'meat',
    'bakery',
    'canned',
    'frozen',
    'pantry',
    'beverages',
    'snacks',
    'condiments',
    'other',
  ];

  const sortedCategories = categoryOrder.filter((cat) => groupedItems[cat]);

  return (
    <div className="space-y-6">
      {sortedCategories.map((category) => (
        <div key={category}>
          {/* Category Header */}
          <div className="mb-3 flex items-center gap-2">
            <h2 className="text-lg font-bold text-white">
              {CATEGORY_LABELS[category]}
            </h2>
            <span className="text-sm text-slate-400 bg-slate-700 px-2 py-1 rounded">
              {groupedItems[category].length}
            </span>
          </div>

          {/* Grid Layout - responsive columns */}
          {viewMode === 'compact' ? (
            <div className="space-y-2">
              {groupedItems[category].map((item) => (
                <ItemRow
                  key={item.id}
                  item={item}
                  onEdit={() => onEdit(item)}
                  onDelete={() => onDelete(item.id)}
                  onQuickUpdateCategory={(value) =>
                    onQuickUpdateCategory?.(item.id, value)
                  }
                  onQuickUpdateQuantity={(value) =>
                    onQuickUpdateQuantity?.(item.id, value)
                  }
                  isDeleting={isDeletingId === item.id}
                  isUpdating={isUpdatingId === item.id}
                />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {groupedItems[category].map((item) => (
                <ItemCard
                  key={item.id}
                  item={item}
                  isExpanded={expandedId === item.id}
                  onToggleExpand={() =>
                    setExpandedId(expandedId === item.id ? null : item.id)
                  }
                  onEdit={() => onEdit(item)}
                  onDelete={() => onDelete(item.id)}
                  onQuickUpdateQuantity={(value) =>
                    onQuickUpdateQuantity?.(item.id, value)
                  }
                  isDeleting={isDeletingId === item.id}
                  isUpdating={isUpdatingId === item.id}
                />
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
