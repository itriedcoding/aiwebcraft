import Link from 'next/link';

export default function Page() {
  return (
    <main className="mx-auto max-w-4xl px-6 py-16">
      <section className="space-y-6 text-center">
        <h1 className="text-5xl font-bold tracking-tight">Build production apps from prompts and designs</h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          An open, developer-first alternative to v0.dev with full code quality, modular architecture, and AI-native tooling.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link href="/studio" className="rounded-md bg-black px-5 py-3 text-white dark:bg-white dark:text-black">
            Open Studio
          </Link>
          <a
            href="https://github.com/"
            target="_blank"
            rel="noreferrer"
            className="rounded-md border px-5 py-3"
          >
            Star on GitHub
          </a>
        </div>
      </section>
    </main>
  );
}