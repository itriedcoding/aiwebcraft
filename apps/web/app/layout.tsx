import './globals.css'

export const metadata = {
  title: 'ACME V0x',
  description: 'Design to app, but 1000x more advanced',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-screen bg-white text-gray-900 antialiased dark:bg-black dark:text-white">
        <div className="mx-auto max-w-7xl px-6 py-6">
          <header className="flex items-center justify-between">
            <a href="/" className="font-semibold">ACME V0x</a>
            <nav className="text-sm">
              <a href="/studio" className="hover:underline">Studio</a>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}