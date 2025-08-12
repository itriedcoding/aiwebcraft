import { NextRequest } from 'next/server';
import { z } from 'zod';
import { generateReactComponentFromPrompt } from '@acme/codegen';
import { createGeneration } from '@acme/db';

const BodySchema = z.object({ prompt: z.string().min(1), temperature: z.number().min(0).max(1).optional(), projectName: z.string().optional() });

export async function POST(req: NextRequest) {
  try {
    const json = await req.json();
    const body = BodySchema.parse(json);
    const code = await generateReactComponentFromPrompt({ prompt: body.prompt, temperature: body.temperature });

    // Persist if DB is configured
    try {
      await createGeneration({ prompt: body.prompt, code, projectName: body.projectName });
    } catch {}

    return new Response(JSON.stringify({ ok: true, code }), { status: 200, headers: { 'content-type': 'application/json' } });
  } catch (err: any) {
    const message = err?.message ?? 'Unknown error';
    return new Response(JSON.stringify({ ok: false, error: message }), { status: 400, headers: { 'content-type': 'application/json' } });
  }
}