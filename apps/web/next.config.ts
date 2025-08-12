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
    "@acme/evals"
  ],
  poweredByHeader: false,
  typescript: {
    ignoreBuildErrors: false
  }
};

export default config;