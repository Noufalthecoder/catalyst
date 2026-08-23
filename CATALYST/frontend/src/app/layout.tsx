import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CATALYST — Industrial Product Intelligence',
  description: 'AI-powered enrichment, verification and normalization for industrial commerce.',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full bg-[#F7F8FA]">
      <body className="min-h-full text-[#111827] antialiased">{children}</body>
    </html>
  );
}
