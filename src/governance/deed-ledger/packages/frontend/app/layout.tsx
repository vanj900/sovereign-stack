import type { Metadata, Viewport } from 'next'
import './globals.css'
import { Providers } from './components/Providers'

export const metadata: Metadata = {
  title: 'Deed Ledger',
  description: 'Portable deed-based reputation ledger',
  manifest: '/manifest.json',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: '#0ea5e9',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
