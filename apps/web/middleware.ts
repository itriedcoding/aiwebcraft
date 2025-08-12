import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { rateLimit } from '@acme/cache';

export async function middleware(req: NextRequest) {
  const ip = req.ip || req.headers.get('x-forwarded-for') || 'unknown';
  const pathname = req.nextUrl.pathname;

  if (pathname.startsWith('/api/')) {
    const key = `${ip}:${pathname}`;
    const { allowed, remaining, resetIn } = await rateLimit({ key, windowSeconds: 10, max: 20 });
    if (!allowed) {
      return new NextResponse(JSON.stringify({ ok: false, error: 'rate_limited', resetIn }), {
        status: 429,
        headers: { 'content-type': 'application/json' },
      });
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/api/:path*'],
};