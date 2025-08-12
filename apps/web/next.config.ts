import type { NextConfig } from 'next';

const config: NextConfig = {
  reactStrictMode: true,
  experimental: {
    optimizePackageImports: ["react", "react-dom"],
    turbo: {
      rules: {}
    }
  },
  transpilePackages: [
    "@acme/ui",
    "@acme/ai",
    "@acme/codegen",
    "@acme/agents",
    "@acme/evals",
    "@acme/db",
    "@acme/logger",
    "@acme/cache"
  ],
  poweredByHeader: false,
  typescript: {
    ignoreBuildErrors: false
  },
  headers: async () => [
    {
      source: "/(.*)",
      headers: [
        { key: "X-Frame-Options", value: "SAMEORIGIN" },
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" }
      ]
    }
  ]
};

export default config;