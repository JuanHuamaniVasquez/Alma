import type { Metadata } from "next";
import { Instrument_Serif, Schibsted_Grotesk, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import { TopBar } from "@/components/TopBar";
import { AlmaProvider } from "@/components/Alma";

const display = Instrument_Serif({ subsets: ["latin"], weight: "400", variable: "--font-display" });
const sans = Schibsted_Grotesk({ subsets: ["latin"], variable: "--font-sans" });
const mono = IBM_Plex_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "ALMA — a ship that keeps its own books",
  description: "Health monitoring for astronauts: every alarm carries its receipt, every claim its preregistration.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${sans.variable} ${mono.variable}`}>
      <body>
        <AlmaProvider>
          <TopBar />
          <main className="absolute inset-x-0 bottom-0 top-11">{children}</main>
        </AlmaProvider>
      </body>
    </html>
  );
}
