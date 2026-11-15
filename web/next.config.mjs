/** @type {import('next').NextConfig} */
export default {
  reactStrictMode: true,
  skipTrailingSlashRedirect: true, // la API de Django usa barra final
  // La vitrina solo LEE del backend Django (DRF, solo GET). Proxy para evitar CORS.
  async rewrites() {
    return [
      { source: "/api/:path*/", destination: "http://127.0.0.1:8000/api/:path*/" }, // DRF exige la barra final
      { source: "/api/:path*", destination: "http://127.0.0.1:8000/api/:path*" },
    ];
  },
  devIndicators: false,
};
