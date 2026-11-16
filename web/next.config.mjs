const apiOrigin = (process.env.ALMA_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
if (process.env.VERCEL && !process.env.ALMA_API_URL) {
  throw new Error("Configura ALMA_API_URL con la URL HTTPS del backend de Render antes de desplegar.");
}
const apiUrl = new URL(apiOrigin);
if (!["http:", "https:"].includes(apiUrl.protocol) || apiUrl.pathname !== "/" || apiUrl.search || apiUrl.hash || apiUrl.username || apiUrl.password) {
  throw new Error("ALMA_API_URL debe ser un origen HTTP(S), sin ruta ni credenciales.");
}
if (process.env.VERCEL && apiUrl.protocol !== "https:") {
  throw new Error("ALMA_API_URL debe usar HTTPS en Vercel.");
}

/** @type {import('next').NextConfig} */
export default {
  reactStrictMode: true,
  skipTrailingSlashRedirect: true, // la API de Django usa barra final
  // Proxy del backend Django: lecturas y captura de ánimo desde el mismo origen.
  async rewrites() {
    return [
      { source: "/api/:path*/", destination: `${apiOrigin}/api/:path*/` }, // DRF exige la barra final
      { source: "/api/:path*", destination: `${apiOrigin}/api/:path*` },
    ];
  },
  devIndicators: false,
};
