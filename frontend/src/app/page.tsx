"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Link from "next/link";

interface Quote {
  symbol: string;
  name: string;
  price: number;
  change_percent: number;
}

export default function Dashboard() {
  const [marketData, setMarketData] = useState<Quote[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await api.get("/market/quotes?symbols=SPY,QQQ,DIA,IWM");
        if (Array.isArray(data)) {
          setMarketData(data);
        } else if (data) {
          setMarketData([data]);
        }
      } catch (err) {
        console.error("Failed to fetch market data:", err);
        setError("Could not connect to backend. Make sure the API is running on port 8000.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const defaultCards = [
    { symbol: "SPY", name: "S&P 500 ETF" },
    { symbol: "QQQ", name: "Nasdaq 100 ETF" },
    { symbol: "DIA", name: "Dow Jones ETF" },
    { symbol: "IWM", name: "Russell 2000 ETF" },
  ];

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 mt-1">Welcome to Alpha Genie - Your AI-powered investment platform</p>
      </div>

      {/* Market Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {loading ? (
          <div className="col-span-4 bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-6">
            <p className="text-gray-400">Loading market data...</p>
          </div>
        ) : error ? (
          <div className="col-span-4 bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-6">
            <p className="text-red-400">{error}</p>
          </div>
        ) : marketData && marketData.length > 0 ? (
          marketData.map((quote) => (
            <div
              key={quote.symbol}
              className={`bg-[#1a1a24] border rounded-xl p-5 ${
                (quote.change_percent || 0) >= 0
                  ? "border-green-500/30"
                  : "border-red-500/30"
              }`}
            >
              <div className="flex justify-between items-start mb-3">
                <span className="text-white font-semibold">{quote.symbol}</span>
                <span
                  className={`text-xs px-2 py-1 rounded-full ${
                    (quote.change_percent || 0) >= 0
                      ? "bg-green-500/20 text-green-400"
                      : "bg-red-500/20 text-red-400"
                  }`}
                >
                  {(quote.change_percent || 0) >= 0 ? "+" : ""}
                  {(quote.change_percent || 0).toFixed(2)}%
                </span>
              </div>
              <p className="text-2xl font-bold text-white">
                ${(quote.price || 0).toFixed(2)}
              </p>
              <p className="text-sm text-gray-500 mt-1">{quote.name}</p>
            </div>
          ))
        ) : (
          defaultCards.map((card) => (
            <div
              key={card.symbol}
              className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-5"
            >
              <div className="flex justify-between items-start mb-3">
                <span className="text-white font-semibold">{card.symbol}</span>
                <span className="text-xs px-2 py-1 rounded-full bg-blue-500/20 text-blue-400">
                  --
                </span>
              </div>
              <p className="text-2xl font-bold text-white">--</p>
              <p className="text-sm text-gray-500 mt-1">{card.name}</p>
            </div>
          ))
        )}
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link href="/documents">
            <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-5 hover:border-blue-500/50 transition-colors cursor-pointer group">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg bg-blue-600/20 flex items-center justify-center">
                  <span className="text-xl">📄</span>
                </div>
                <h3 className="text-white font-medium group-hover:text-blue-400 transition-colors">
                  Upload Document
                </h3>
              </div>
              <p className="text-gray-500 text-sm">
                Analyze earnings calls, filings, and research reports
              </p>
            </div>
          </Link>

          <Link href="/portfolio">
            <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-5 hover:border-blue-500/50 transition-colors cursor-pointer group">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg bg-green-600/20 flex items-center justify-center">
                  <span className="text-xl">💼</span>
                </div>
                <h3 className="text-white font-medium group-hover:text-blue-400 transition-colors">
                  View Portfolio
                </h3>
              </div>
              <p className="text-gray-500 text-sm">
                Track your holdings and performance
              </p>
            </div>
          </Link>

          <Link href="/market">
            <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-5 hover:border-blue-500/50 transition-colors cursor-pointer group">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg bg-purple-600/20 flex items-center justify-center">
                  <span className="text-xl">📈</span>
                </div>
                <h3 className="text-white font-medium group-hover:text-blue-400 transition-colors">
                  Market Research
                </h3>
              </div>
              <p className="text-gray-500 text-sm">
                Search for stocks and view charts
              </p>
            </div>
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-5">
          <h3 className="text-gray-400 text-sm mb-2">AI Insights Today</h3>
          <p className="text-3xl font-bold text-white">--</p>
          <p className="text-sm text-blue-400 mt-2">Connect LLM to enable</p>
        </div>
        <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-5">
          <h3 className="text-gray-400 text-sm mb-2">Documents Analyzed</h3>
          <p className="text-3xl font-bold text-white">0</p>
          <p className="text-sm text-gray-500 mt-2">Upload documents to get started</p>
        </div>
      </div>
    </div>
  );
}
