/** @type {import('next').NextConfig} */

if (!process.env.NEXT_PUBLIC_API_URL) {
  throw new Error(
    "[Config Error] NEXT_PUBLIC_API_URL is not defined.\n" +
    "Set it in .env.local for development:\n" +
    "  NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1\n" +
    "Or provide it via your CI/CD environment for staging/production."
  );
}

const nextConfig = {
  reactStrictMode: true,
};

export default nextConfig;
