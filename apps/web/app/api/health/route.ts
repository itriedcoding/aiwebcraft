export async function GET() {
  return new Response(
    JSON.stringify({ ok: true, uptime: process.uptime() }),
    { status: 200, headers: { 'content-type': 'application/json' } }
  );
}