export function GET() {
  return new Response(
    `User-agent: *\nAllow: /\nSitemap: ${process.env.NEXT_PUBLIC_APP_URL ?? 'http://localhost:3000'}/sitemap.xml\n`,
    { status: 200, headers: { 'content-type': 'text/plain' } }
  );
}