import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { TopBar } from "@/components/TopBar";
import { AlmaProvider } from "@/components/Alma";
import { ShipProvider } from "@/components/Ship";

// Tipografías LOCALES (OFL: Instrument Serif, Schibsted Grotesk, IBM Plex Mono; subconjunto latino): la demo no depende de internet.
const display = localFont({ src: "../fonts/instrument-serif-400.woff2", weight: "400", variable: "--font-display" });
const sans = localFont({ src: "../fonts/schibsted-grotesk-var.woff2", weight: "400 900", variable: "--font-sans" });
const mono = localFont({ src: [{ path: "../fonts/plex-mono-400.woff2", weight: "400" }, { path: "../fonts/plex-mono-500.woff2", weight: "500" }], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "ALMA — a ship that keeps its own books",
  description: "Health monitoring for astronauts: every alarm carries its receipt, every claim its preregistration.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${sans.variable} ${mono.variable}`}>
      <body>
        <AlmaProvider>
          <ShipProvider>
            <TopBar />
            <main className="absolute inset-x-0 bottom-0 top-11">{children}</main>
          </ShipProvider>
        </AlmaProvider>
      </body>
    </html>
  );
}
