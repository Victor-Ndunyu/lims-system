/** @type {import('next').NextConfig} */
const portalMode = process.env.NEXT_PUBLIC_PORTAL_MODE;

const nextConfig = {
  reactStrictMode: true,
  distDir: portalMode ? `.next-${portalMode}` : ".next",
  async redirects() {
    if (portalMode === "public") {
      return [
        {
          source: "/",
          destination: "/public",
          permanent: false,
        },
        {
          source: "/admin/:path*",
          destination: "/public",
          permanent: false,
        },
      ];
    }

    if (portalMode === "admin") {
      return [
        {
          source: "/",
          destination: "/admin",
          permanent: false,
        },
        {
          source: "/public/:path*",
          destination: "/admin",
          permanent: false,
        },
      ];
    }

    return [];
  },
};

module.exports = nextConfig;
