import type { Metadata } from "next";
import "./globals.css";
import AppShell from "@/features/shared/components/layout/AppShell";
import { Geist } from "next/font/google";
import QueryProvider from "@/features/shared/providers/QueryProvider";

export const metadata: Metadata = {
  title: "F1 Lightning McQueen — Formula 1 Intelligence Platform",
  description:
    "Advanced F1 analytics, driver insights, constructor analysis, circuit intelligence, and championship forecasting.",
  keywords: [
    "Formula 1",
    "F1 Analytics",
    "Driver Statistics",
    "Constructor Analysis",
    "Race Intelligence",
  ],
};

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${geist.variable} font-sans`}>
        <QueryProvider>
          <AppShell>{children}</AppShell>
        </QueryProvider>
      </body>
    </html>
  );
}
