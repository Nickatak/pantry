'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getProfile, clearTokens, getAccessToken, getItems, updateItem, deleteItem, type Item, type User } from '../lib/api';
import { SearchBar, ItemsList, EditItemModal, CategoryFilter } from './components';

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [pageSize] = useState(20);
  const [viewMode, setViewMode] = useState<'compact' | 'cards'>('compact');
  const [editingItem, setEditingItem] = useState<Item | null>(null);
  const [isSavingEdit, setIsSavingEdit] = useState(false);
  const [isDeletingId, setIsDeletingId] = useState<number | null>(null);
  const [isUpdatingId, setIsUpdatingId] = useState<number | null>(null);
  const router = useRouter();

  // Fetch user profile
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const accessToken = getAccessToken();
        if (!accessToken) {
          router.push('/login');
          return;
        }

        const data = await getProfile();
        setUser(data);
      } catch {
        setError('Failed to load profile. Please log in again.');
        clearTokens();
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [router]);

  // Fetch items whenever page or search changes
  useEffect(() => {
    if (!user) return;

    const fetchItems = async () => {
      setItemsLoading(true);
      try {
        const response = await getItems(currentPage, pageSize, searchQuery);
        // Filter by category if one is selected
        let filteredItems = response.results;
        if (selectedCategory) {
          filteredItems = response.results.filter(item => item.category === selectedCategory);
        }
        setItems(filteredItems);
        setTotalItems(response.count);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load items');
      } finally {
        setItemsLoading(false);
      }
    };

    fetchItems();
  }, [user, currentPage, searchQuery, pageSize, selectedCategory]);

  const handleLogout = () => {
    clearTokens();
    router.push('/');
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    setCurrentPage(1); // Reset to first page on search
  };

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    setCurrentPage(1); // Reset to first page on category change
  };

  const handleEditItem = async (data: { title: string; description: string; alias: string; category: string }) => {
    if (!editingItem) return;

    setIsSavingEdit(true);
    try {
      const updated = await updateItem(editingItem.id, data);
      if (selectedCategory && updated.category !== selectedCategory) {
        setItems(items.filter(item => item.id !== updated.id));
      } else {
        setItems(items.map(item => item.id === updated.id ? updated : item));
      }
      setEditingItem(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update item');
    } finally {
      setIsSavingEdit(false);
    }
  };

  const handleDeleteItem = async (id: number) => {
    if (!confirm('Are you sure you want to delete this item?')) return;

    setIsDeletingId(id);
    try {
      await deleteItem(id);
      setItems(items.filter(item => item.id !== id));
      setTotalItems(totalItems - 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete item');
    } finally {
      setIsDeletingId(null);
    }
  };

  const handleQuickUpdateCategory = async (id: number, category: string) => {
    setIsUpdatingId(id);
    try {
      const updated = await updateItem(id, { category });
      if (selectedCategory && updated.category !== selectedCategory) {
        setItems(items.filter(item => item.id !== updated.id));
      } else {
        setItems(items.map(item => item.id === updated.id ? updated : item));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update item');
    } finally {
      setIsUpdatingId(null);
    }
  };

  const handleQuickUpdateQuantity = async (id: number, quantity: number) => {
    setIsUpdatingId(id);
    try {
      const updated = await updateItem(id, { quantity });
      if (selectedCategory && updated.category !== selectedCategory) {
        setItems(items.filter(item => item.id !== updated.id));
      } else {
        setItems(items.map(item => item.id === updated.id ? updated : item));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update item');
    } finally {
      setIsUpdatingId(null);
    }
  };

  const totalPages = Math.ceil(totalItems / pageSize);

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="text-white text-xl">Loading...</div>
      </main>
    );
  }

  if (error && !user) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="text-red-400 text-xl">{error}</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <nav className="bg-slate-950 text-white p-4 flex justify-between items-center border-b border-slate-700">
        <h1 className="text-2xl font-bold">Pantry Dashboard</h1>
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded transition-colors"
        >
          Logout
        </button>
      </nav>

      <div className="container mx-auto p-8">
        {/* User Welcome Card */}
        <div className="bg-slate-800 rounded-lg shadow-xl p-6 mb-8 border border-slate-700">
          <h2 className="text-2xl font-bold mb-4 text-white">Welcome, {user?.email}!</h2>
          <button
            onClick={() => router.push('/barcode')}
            className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Scan Barcode
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-red-900/20 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Items Section */}
        <div className="bg-slate-800 rounded-lg shadow-xl p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">Items ({totalItems})</h3>
            <div className="flex items-center gap-3">
              {totalItems > 0 && (
                <span className="text-sm text-slate-400">
                  Page {currentPage} of {Math.ceil(totalItems / pageSize)}
                </span>
              )}
              <div className="flex rounded-lg overflow-hidden border border-slate-700">
                <button
                  onClick={() => setViewMode('compact')}
                  className={`px-3 py-2 text-sm font-medium transition-colors ${
                    viewMode === 'compact'
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 text-slate-200 hover:bg-slate-600'
                  }`}
                >
                  Compact
                </button>
                <button
                  onClick={() => setViewMode('cards')}
                  className={`px-3 py-2 text-sm font-medium transition-colors ${
                    viewMode === 'cards'
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 text-slate-200 hover:bg-slate-600'
                  }`}
                >
                  Cards
                </button>
              </div>
            </div>
          </div>

          <div className="sticky top-20 z-20 -mx-6 px-6 py-4 mb-6 bg-slate-900/90 backdrop-blur border-b border-slate-700">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1">
                <SearchBar
                  value={searchQuery}
                  onChange={handleSearch}
                  placeholder="Search by title, barcode, or description..."
                />
              </div>
              <button
                onClick={() => router.push('/barcode')}
                className="px-5 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Scan Barcode
              </button>
            </div>

            <div className="mt-3">
              <CategoryFilter
                selectedCategory={selectedCategory}
                onChange={handleCategoryChange}
              />
            </div>
          </div>

          <ItemsList
            items={items}
            onEdit={setEditingItem}
            onDelete={handleDeleteItem}
            onQuickUpdateCategory={handleQuickUpdateCategory}
            onQuickUpdateQuantity={handleQuickUpdateQuantity}
            isLoading={itemsLoading}
            isDeletingId={isDeletingId}
            isUpdatingId={isUpdatingId}
            viewMode={viewMode}
          />

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded transition-colors"
              >
                Previous
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`px-4 py-2 rounded transition-colors ${
                    currentPage === page
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 hover:bg-slate-600 text-white'
                  }`}
                >
                  {page}
                </button>
              ))}
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Edit Item Modal */}
      <EditItemModal
        item={editingItem}
        isOpen={editingItem !== null}
        onClose={() => setEditingItem(null)}
        onSave={handleEditItem}
        isSaving={isSavingEdit}
      />
    </main>
  );
}
