"use client";
import { useState } from 'react';
import { Button } from '@acme/ui';
import { GeneratedPreview } from '../../components/GeneratedPreview';

export default function StudioPage() {
  const [prompt, setPrompt] = useState('A pricing card with three tiers and a toggle for monthly/annual');
  const [loading, setLoading] = useState(false);
  const [code, setCode] = useState('');
  const [error, setError] = useState<string | null>(null);

  async function onGenerate() {
    setLoading(true);
    setError(null);
    setCode('');
    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });
      const data = await res.json();
      if (!data.ok) throw new Error(data.error || 'Failed to generate');
      setCode(data.code);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <h1 className="text-3xl font-semibold">Studio</h1>
      <p className="mt-2 text-gray-600 dark:text-gray-400">
        Prompt, paste Figma links, generate, edit, and ship.
      </p>

      <div className="mt-6 grid gap-4">
        <textarea
          className="w-full min-h-[120px] rounded-md border p-3"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <div className="flex items-center gap-3">
          <Button onClick={onGenerate} disabled={loading}>
            {loading ? 'Generating…' : 'Generate Component'}
          </Button>
        </div>
      </div>

      {error && <p className="mt-4 text-red-600">{error}</p>}

      {code && (
        <section className="mt-8">
          <h2 className="mb-2 text-xl font-semibold">Generated TSX</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <pre className="overflow-auto rounded-md border bg-neutral-50 p-4 text-sm dark:bg-neutral-900">
              <code>{code}</code>
            </pre>
            <div className="rounded-md border p-2">
              <GeneratedPreview code={code} />
            </div>
          </div>
        </section>
      )}
    </main>
  );
}