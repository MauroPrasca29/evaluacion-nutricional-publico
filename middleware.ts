import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value || 
                request.headers.get('authorization')?.replace('Bearer ', '')
  
  const isAuthPage = request.nextUrl.pathname.startsWith('/login') || 
                     request.nextUrl.pathname.startsWith('/register')
  
  const isPublicPath = request.nextUrl.pathname.startsWith('/api/auth-login') ||
                       request.nextUrl.pathname.startsWith('/api/auth-register') ||
                       request.nextUrl.pathname.startsWith('/api/')
  
  // Si no hay token y no está en página de auth, redirigir a login
  if (!token && !isAuthPage && !isPublicPath) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  
  // Si hay token y está en página de auth, redirigir al dashboard
  if (token && isAuthPage) {
    return NextResponse.redirect(new URL('/', request.url))
  }
  
  return NextResponse.next()
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
}
