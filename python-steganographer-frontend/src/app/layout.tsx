import type { Metadata } from "next";

import "./globals.css";
import Footer from "@/components/Footer";
import Navigation from "@/components/Navigation";

export const metadata: Metadata = {
  title: "Python Steganographer",
  description: "FastAPI based steganography server.",
  keywords: [
    "steganography",
    "lsb",
    "dct",
    "fastapi",
    "python",
    "image processing",
  ],
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-background">
          <Navigation />
          <main className="container mx-auto px-4 py-8 max-w-6xl pb-20">
            {children}
          </main>
          <Footer />
        </div>
      </body>
    </html>
  );
}
