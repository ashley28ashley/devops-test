import type { Metadata, Viewport } from "next"
import { Inter, JetBrains_Mono } from "next/font/google"
import { SidebarNav } from "@/components/sidebar-nav"
import "./globals.css"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
})

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
})

export const metadata: Metadata = {
  title: "Cultural Events Paris - Dashboard",
  description:
    "Dashboard de visualisation des evenements culturels parisiens. Pipeline DevOps: MongoDB, PostgreSQL, FastAPI, React.",
}

export const viewport: Viewport = {
  themeColor: "#1a1a2e",
  width: "device-width",
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr" className={`${inter.variable} ${jetbrains.variable}`}>
      <body className="font-sans antialiased">
        <SidebarNav />
        <main className="min-h-screen lg:pl-64">
          <div className="px-4 py-6 pt-16 lg:px-8 lg:pt-6">{children}</div>
        </main>
      </body>
    </html>
  )
}
