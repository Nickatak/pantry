import { NextRequest, NextResponse } from 'next/server';

/**
 * Middleware to handle authentication redirects
 * Runs before the page renders, preventing race conditions
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Public routes that don't require authentication
  const publicRoutes = ['/login', '/register'];

  // Check if path is public
  const isPublicRoute = publicRoutes.includes(pathname);

  // Get access token from cookies
  const token = request.cookies.get('accessToken')?.value;

  // If accessing public route, always allow
  if (isPublicRoute) {
    return NextResponse.next();
  }

  // If accessing protected route without token, redirect to login
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Token exists, allow access
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
