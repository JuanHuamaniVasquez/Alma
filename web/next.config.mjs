/** @type {import('next').NextConfig} */
export default {
  reactStrictMode: true,
  // La vitrina solo LEE del backend Django (DRF, solo GET). Proxy para evitar CORS.
  async rewrites() { return [{ source: "/api/:path*", destination: "http://127.0.0.1:8000/api/:path*" }]; },
};
