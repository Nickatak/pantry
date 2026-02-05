'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getProfile, clearTokens, getAccessToken } from '../lib/api';

interface User {
  id: number;
  email: string;
}

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

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
      } catch (err) {
        clearTokens();
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [router]);

  const handleLogout = () => {
    clearTokens();
    router.push('/');
  };

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="text-white text-xl">Loading...</div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="text-red-400 text-xl">{error}</div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <nav className="bg-slate-950 text-white p-4 flex justify-between items-center border-b border-slate-700">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button
          onClick={handleLogout}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded transition-colors"
        >
          Logout
        </button>
      </nav>

      <div className="container mx-auto p-8">
        <div className="bg-slate-800 rounded-lg shadow-xl p-8 max-w-2xl border border-slate-700">
          <h2 className="text-3xl font-bold mb-6 text-white">Welcome, {user?.email}!</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300">Email</label>
              <p className="text-lg text-slate-100">{user?.email}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300">User ID</label>
              <p className="text-lg text-slate-100">{user?.id}</p>
            </div>
          </div>

          <div className="mt-8 p-4 bg-blue-900/20 rounded-lg border-l-4 border-blue-500">
            <p className="text-slate-300">
              You are successfully logged in! This is your dashboard.
            </p>
          </div>
        </div>
      </div>    </main>
  );
}
