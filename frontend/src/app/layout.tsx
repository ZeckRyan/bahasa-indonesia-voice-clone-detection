import type { Metadata } from "next";
import { Inter, Montserrat, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const montserrat = Montserrat({ subsets: ["latin"], variable: "--font-montserrat" });
const jetbrains = JetBrains_Mono({ subsets: ["latin"], variable: "--font-jetbrains" });

export const metadata: Metadata = {
  title: "VoiceGuard — Deteksi Deepfake Audio",
  description: "Forensik Akustik Berbasis Kecerdasan Buatan untuk Mendeteksi Voice Cloning",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className="scroll-smooth">
      <body className={`${inter.variable} ${montserrat.variable} ${jetbrains.variable} font-sans antialiased bg-white text-slate-800`}>
        {children}
      </body>
    </html>
  );
}
