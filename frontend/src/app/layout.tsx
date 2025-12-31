import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "InfronAI - Intelligent GCP Architecture Advisor",
  description: "AI-powered infrastructure recommendations for Google Cloud Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
