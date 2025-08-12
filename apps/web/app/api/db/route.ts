import { getPrisma } from '@acme/db';

export async function GET() {
  try {
    const prisma = getPrisma();
    const count = await prisma.project.count();
    return new Response(JSON.stringify({ ok: true, projects: count }), {
      status: 200,
      headers: { 'content-type': 'application/json' },
    });
  } catch (e: any) {
    return new Response(JSON.stringify({ ok: false, error: e.message || 'db error' }), {
      status: 500,
      headers: { 'content-type': 'application/json' },
    });
  }
}