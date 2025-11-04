import "@/styles/globals.css";
import { Toaster } from "@/components/ui/sonner"

import { type Metadata } from "next";
import { Geist } from "next/font/google";

export const metadata: Metadata = {
  title: "POS System - Point of Sale Management",
  description: "Modern point of sale system for retail businesses. Manage products, process orders, track inventory, and handle customer transactions.",
  keywords: ["POS", "Point of Sale", "Retail", "Inventory", "Orders", "Products"],
  authors: [{ name: "POS System Team" }],
  icons: [{ rel: "icon", url: "/favicon.ico" }],
};

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${geist.variable}`}>
      <body>
         <main>{children}</main>
        <Toaster richColors position="top-right"/>
      </body>
    </html>
  );
}
