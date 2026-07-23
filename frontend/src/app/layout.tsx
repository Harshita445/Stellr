import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Stellr",
  description: "Your people. Your time. Aligned.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
