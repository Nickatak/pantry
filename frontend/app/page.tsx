'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getAccessToken } from './lib/api';

export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      // Middleware will redirect, but we also redirect here as fallback
      router.push('/login');
    } else {
      // Token exists, redirect to dashboard
      router.push('/dashboard');
    }
    setIsLoading(false);
  }, [router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="animate-pulse">
          <h1 className="text-5xl font-bold text-slate-500">Pantry</h1>
        </div>
      </main>
    );
  }

  // This should not be visible as we redirect above, but show as fallback
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="text-center">
        <h1 className="text-5xl font-bold text-white mb-4">Welcome to Pantry</h1>
        <p className="text-xl text-slate-300 mb-8">A fresh start</p>
      </div>
    </main>
  );
}
