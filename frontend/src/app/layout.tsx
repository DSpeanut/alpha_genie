import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import ChatPanel from "@/components/ChatPanel";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Alpha Genie",
  description: "AI-powered asset management platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-[#0a0a0f]`}>
        <div className="flex h-screen">
          {/* Left Sidebar - Navigation */}
          <Sidebar />

          {/* Main Content Area */}
          <main className="flex-1 overflow-auto p-6 bg-[#0a0a0f]">
            {children}
          </main>

          {/* Right Panel - AI Chat */}
          <ChatPanel />
        </div>
      </body>
    </html>
  );
}
