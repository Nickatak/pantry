'use client';

const CATEGORIES = [
  { value: '', label: 'All Items' },
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

export function CategoryFilter({
  selectedCategory,
  onChange,
}: {
  selectedCategory: string;
  onChange: (category: string) => void;
}) {
  return (
    <div className="w-full overflow-x-auto">
      <div className="flex gap-2 pb-2 min-w-min">
        {CATEGORIES.map((category) => (
          <button
            key={category.value}
            onClick={() => onChange(category.value)}
            className={`px-4 py-3 rounded-full font-semibold text-sm sm:text-base whitespace-nowrap transition-all flex-shrink-0 ${
              selectedCategory === category.value
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            {category.label}
          </button>
        ))}
      </div>
    </div>
  );
}
