import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Fintendo Research",
  description: "AI-powered equity research platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
