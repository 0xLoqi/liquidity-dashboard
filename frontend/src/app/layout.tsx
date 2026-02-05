import type { Metadata } from "next";
import { DM_Sans, IBM_Plex_Mono } from "next/font/google";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
});

const ibmPlexMono = IBM_Plex_Mono({
  variable: "--font-ibm-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  icons: {
    icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌊</text></svg>",
  },
  title: "FlowState — Crypto Liquidity Regime Tracker",
  description:
    "Track 5 macro liquidity indicators to know when crypto conditions favor risk-on vs playing defense.",
  openGraph: {
    title: "FlowState — Crypto Liquidity Regime Tracker",
    description:
      "Track 5 macro liquidity indicators to know when crypto conditions favor risk-on vs playing defense.",
    url: "https://flowstate-dashboard.vercel.app",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "FlowState — Crypto Liquidity Regime Tracker",
    description:
      "Track 5 macro liquidity indicators to know when crypto conditions favor risk-on vs playing defense.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${dmSans.variable} ${ibmPlexMono.variable} antialiased noise-bg`}
      >
        {children}
      </body>
    </html>
  );
}
