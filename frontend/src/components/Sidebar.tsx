"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { name: "Dashboard", href: "/", icon: "📊" },
  { name: "Documents", href: "/documents", icon: "📄" },
  { name: "Market", href: "/market", icon: "📈" },
  { name: "Portfolio", href: "/portfolio", icon: "💼" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="w-64 bg-[#0d0d14] border-r border-[#1e1e2e] flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-[#1e1e2e]">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <span className="text-2xl">⚡</span>
          <span className="bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">
            Alpha Genie
          </span>
        </h1>
        <p className="text-sm text-gray-500 mt-1">Investment Platform</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                      : "text-gray-400 hover:bg-[#1a1a24] hover:text-white"
                  }`}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span className="font-medium">{item.name}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-[#1e1e2e]">
        <div className="flex items-center gap-3 px-4 py-2">
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-medium">
            AG
          </div>
          <div>
            <p className="text-sm text-white">Alpha Genie</p>
            <p className="text-xs text-gray-500">v0.1.0</p>
          </div>
        </div>
      </div>
    </div>
  );
}
