'use client';

import { useState, useEffect } from 'react';
import { Item } from '../lib/api';

const CATEGORIES = [
  { value: 'produce', label: '🥬 Produce' },
  { value: 'dairy', label: '🧈 Dairy' },
  { value: 'meat', label: '🥩 Meat & Poultry' },
  { value: 'bakery', label: '🍞 Bakery' },
  { value: 'canned', label: '🥫 Canned Goods' },
  { value: 'frozen', label: '🧊 Frozen' },
  { value: 'pantry', label: '📦 Pantry Staples' },
  { value: 'beverages', label: '🥤 Beverages' },
  { value: 'snacks', label: '🍿 Snacks' },
  { value: 'condiments', label: '🍯 Condiments & Sauces' },
  { value: 'other', label: '📌 Other' },
];

export function EditItemModal({
  item,
  isOpen,
  onClose,
  onSave,
  isSaving = false,
}: {
  item: Item | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: { title: string; description: string; alias: string; category: string }) => void;
  isSaving?: boolean;
}) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    alias: '',
    category: 'other',
  });

  useEffect(() => {
    if (item) {
      setFormData({
        title: item.title,
        description: item.description,
        alias: item.alias,
        category: item.category || 'other',
      });
    }
  }, [item, isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  if (!isOpen || !item) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold text-white mb-4">Edit Item</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Title
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) =>
                setFormData({ ...formData, title: e.target.value })
              }
              className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded-lg focus:outline-none focus:border-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Category
            </label>
            <select
              value={formData.category}
              onChange={(e) =>
                setFormData({ ...formData, category: e.target.value })
              }
              className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded-lg focus:outline-none focus:border-blue-500"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Alias (Optional)
            </label>
            <input
              type="text"
              value={formData.alias}
              onChange={(e) =>
                setFormData({ ...formData, alias: e.target.value })
              }
              className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Description (Optional)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              rows={4}
              className="w-full px-3 py-2 bg-slate-700 text-white border border-slate-600 rounded-lg focus:outline-none focus:border-blue-500 resize-none"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isSaving}
              className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white font-medium rounded transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded transition-colors disabled:opacity-50"
            >
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
