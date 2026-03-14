import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "GPS AIedu Web Chat",
  description: "Chat + auto-log to Google Sheets Raw Data"
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
