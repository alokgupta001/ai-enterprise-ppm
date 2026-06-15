import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Navbar from "@/components/Navbar";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI-Powered Enterprise PPM Platform",
  description: "Assess PPM maturity, manage portfolios, and get AI root cause analysis dashboard.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased dark`}>
      <body className="h-full bg-zinc-950 text-zinc-100 flex flex-row overflow-hidden font-sans">
        <Navbar />
        <main className="flex-1 flex flex-col min-w-0 bg-zinc-900 overflow-y-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
