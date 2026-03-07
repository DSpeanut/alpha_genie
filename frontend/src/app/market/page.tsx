"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";

interface Quote {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  market_cap: number;
  pe_ratio: number;
  sector: string;
  industry: string;
  fifty_two_week_high: number;
  fifty_two_week_low: number;
}

interface HistoryPoint {
  date: string;
  close: number;
  volume: number;
}

interface SentenceSample {
  text: string;
  score: number;
}

interface SentimentData {
  positive: number;
  neutral: number;
  negative: number;
  sentences_analyzed: number;
  top_positive_sentences: SentenceSample[];
  top_neutral_sentences: SentenceSample[];
  top_negative_sentences: SentenceSample[];
}

// Format quarter for display (2025Q4 -> "Q4 2025")
function formatQuarter(quarter: string): string {
  const match = quarter.match(/(\d{4})Q(\d)/);
  if (match) {
    return `Q${match[2]} ${match[1]}`;
  }
  return quarter;
}

export default function MarketPage() {
  const [symbol, setSymbol] = useState("");
  const [quarter, setQuarter] = useState("latest");
  const [actualQuarter, setActualQuarter] = useState<string | null>(null);
  const [quote, setQuote] = useState<Quote | null>(null);
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [sentiment, setSentiment] = useState<SentimentData | null>(null);
  const [loading, setLoading] = useState(false);
  const [sentimentLoading, setSentimentLoading] = useState(false);
  const [expandedSentiment, setExpandedSentiment] = useState<string | null>(null);
  const [recentQuarters, setRecentQuarters] = useState<string[]>([]);

  useEffect(() => {
    api.get("/earnings/quarters").then(setRecentQuarters).catch(() => {});
  }, []);

  const searchSymbol = async () => {
    if (!symbol.trim()) return;

    setLoading(true);
    setSentiment(null);
    setActualQuarter(null);
    try {
      const [quoteData, historyData] = await Promise.all([
        api.get(`/market/quote/${symbol}`),
        api.get(`/market/history/${symbol}?period=1mo&interval=1d`),
      ]);
      setQuote(quoteData);
      setHistory(Array.isArray(historyData) ? historyData : []);
    } catch (error) {
      alert(`Failed to fetch data: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const analyzeSentiment = async () => {
    if (!symbol.trim()) return;

    setSentimentLoading(true);
    setActualQuarter(null);
    try {
      const data = await api.get(`/earnings/analyze/${symbol}?quarter=${quarter}`);
      setSentiment(data.sentiment);
      setActualQuarter(data.quarter);  // Store the actual quarter found
    } catch (error) {
      alert(`Failed to analyze sentiment: ${error}`);
    } finally {
      setSentimentLoading(false);
    }
  };

  const formatNumber = (num: number | undefined) => {
    if (!num) return "N/A";
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    return `$${num.toLocaleString()}`;
  };

  const getSentimentColor = (type: string, value: number) => {
    if (type === "positive") return "text-green-400";
    if (type === "negative") return "text-red-400";
    return "text-gray-400";
  };

  const getSentimentBarColor = (type: string) => {
    if (type === "positive") return "bg-green-500";
    if (type === "negative") return "bg-red-500";
    return "bg-gray-500";
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Market Research</h1>
        <p className="text-gray-400 mt-1">Search for stocks and view market data</p>
      </div>

      {/* Search */}
      <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-5 mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Enter symbol (e.g., AAPL)"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            onKeyPress={(e) => e.key === "Enter" && searchSymbol()}
            className="flex-1 px-4 py-2 bg-[#0a0a0f] border border-[#2a2a3a] text-white placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={searchSymbol}
            disabled={loading}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${
              loading
                ? "bg-gray-700 text-gray-400 cursor-not-allowed"
                : "bg-blue-600 text-white hover:bg-blue-700"
            }`}
          >
            {loading ? "Loading..." : "Search"}
          </button>
        </div>
      </div>

      {/* Quote Details */}
      {quote && (
        <>
          <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-6 mb-6">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-2xl font-bold text-white">{quote.symbol}</h2>
                <p className="text-gray-400">{quote.name}</p>
                <p className="text-4xl font-bold text-white mt-4">
                  ${quote.price?.toFixed(2)}
                </p>
                <span className={`inline-block mt-2 px-3 py-1 rounded-full text-sm ${
                  (quote.change_percent || 0) >= 0
                    ? "bg-green-500/20 text-green-400"
                    : "bg-red-500/20 text-red-400"
                }`}>
                  {(quote.change_percent || 0) >= 0 ? "+" : ""}
                  {quote.change_percent?.toFixed(2)}% (${quote.change?.toFixed(2)})
                </span>
              </div>
              <div className="text-right">
                <p className="text-gray-500">Sector: <span className="text-gray-300">{quote.sector || "N/A"}</span></p>
                <p className="text-gray-500">Industry: <span className="text-gray-300">{quote.industry || "N/A"}</span></p>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-[#0a0a0f] border border-[#2a2a3a] rounded-lg p-4">
                <p className="text-gray-500 text-sm">Market Cap</p>
                <p className="text-white font-semibold text-lg">{formatNumber(quote.market_cap)}</p>
              </div>
              <div className="bg-[#0a0a0f] border border-[#2a2a3a] rounded-lg p-4">
                <p className="text-gray-500 text-sm">P/E Ratio</p>
                <p className="text-white font-semibold text-lg">{quote.pe_ratio?.toFixed(2) || "N/A"}</p>
              </div>
              <div className="bg-[#0a0a0f] border border-[#2a2a3a] rounded-lg p-4">
                <p className="text-gray-500 text-sm">52W High</p>
                <p className="text-green-400 font-semibold text-lg">${quote.fifty_two_week_high?.toFixed(2)}</p>
              </div>
              <div className="bg-[#0a0a0f] border border-[#2a2a3a] rounded-lg p-4">
                <p className="text-gray-500 text-sm">52W Low</p>
                <p className="text-red-400 font-semibold text-lg">${quote.fifty_two_week_low?.toFixed(2)}</p>
              </div>
            </div>
          </div>

          {/* Earnings Sentiment Analysis */}
          <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-white">Earnings Call Sentiment</h3>
              <div className="flex gap-3">
                <select
                  value={quarter}
                  onChange={(e) => setQuarter(e.target.value)}
                  className="px-3 py-2 bg-[#0a0a0f] border border-[#2a2a3a] text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="latest">Latest Available</option>
                  {recentQuarters.map((q) => (
                    <option key={q} value={q}>
                      {formatQuarter(q)}
                    </option>
                  ))}
                </select>
                <button
                  onClick={analyzeSentiment}
                  disabled={sentimentLoading}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    sentimentLoading
                      ? "bg-gray-700 text-gray-400 cursor-not-allowed"
                      : "bg-blue-600 text-white hover:bg-blue-700"
                  }`}
                >
                  {sentimentLoading ? "Analyzing..." : "Analyze"}
                </button>
              </div>
            </div>

            {sentiment ? (
              <div className="space-y-4">
                {/* Sentiment Bars with Expandable Samples */}
                <div className="space-y-3">
                  {/* Positive */}
                  <div>
                    <button
                      onClick={() => setExpandedSentiment(expandedSentiment === 'positive' ? null : 'positive')}
                      className="w-full text-left"
                    >
                      <div className="flex justify-between mb-1 items-center">
                        <span className="text-green-400 text-sm font-medium flex items-center gap-2">
                          Positive
                          <span className="text-xs text-gray-500">
                            {expandedSentiment === 'positive' ? '▼' : '▶'}
                          </span>
                        </span>
                        <span className="text-green-400 text-sm font-bold">{(sentiment.positive * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-[#2a2a3a] rounded-full h-3">
                        <div
                          className="bg-green-500 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${sentiment.positive * 100}%` }}
                        />
                      </div>
                    </button>
                    {expandedSentiment === 'positive' && sentiment.top_positive_sentences && (
                      <div className="mt-2 space-y-2 pl-2 border-l-2 border-green-500/30">
                        {sentiment.top_positive_sentences.map((s, i) => (
                          <div key={i} className="bg-[#0a0a0f] rounded-lg p-3">
                            <p className="text-gray-300 text-sm">{s.text}</p>
                            <p className="text-green-400 text-xs mt-1">Score: {(s.score * 100).toFixed(1)}%</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Neutral */}
                  <div>
                    <button
                      onClick={() => setExpandedSentiment(expandedSentiment === 'neutral' ? null : 'neutral')}
                      className="w-full text-left"
                    >
                      <div className="flex justify-between mb-1 items-center">
                        <span className="text-gray-400 text-sm font-medium flex items-center gap-2">
                          Neutral
                          <span className="text-xs text-gray-500">
                            {expandedSentiment === 'neutral' ? '▼' : '▶'}
                          </span>
                        </span>
                        <span className="text-gray-400 text-sm font-bold">{(sentiment.neutral * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-[#2a2a3a] rounded-full h-3">
                        <div
                          className="bg-gray-500 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${sentiment.neutral * 100}%` }}
                        />
                      </div>
                    </button>
                    {expandedSentiment === 'neutral' && sentiment.top_neutral_sentences && (
                      <div className="mt-2 space-y-2 pl-2 border-l-2 border-gray-500/30">
                        {sentiment.top_neutral_sentences.map((s, i) => (
                          <div key={i} className="bg-[#0a0a0f] rounded-lg p-3">
                            <p className="text-gray-300 text-sm">{s.text}</p>
                            <p className="text-gray-400 text-xs mt-1">Score: {(s.score * 100).toFixed(1)}%</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Negative */}
                  <div>
                    <button
                      onClick={() => setExpandedSentiment(expandedSentiment === 'negative' ? null : 'negative')}
                      className="w-full text-left"
                    >
                      <div className="flex justify-between mb-1 items-center">
                        <span className="text-red-400 text-sm font-medium flex items-center gap-2">
                          Negative
                          <span className="text-xs text-gray-500">
                            {expandedSentiment === 'negative' ? '▼' : '▶'}
                          </span>
                        </span>
                        <span className="text-red-400 text-sm font-bold">{(sentiment.negative * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-[#2a2a3a] rounded-full h-3">
                        <div
                          className="bg-red-500 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${sentiment.negative * 100}%` }}
                        />
                      </div>
                    </button>
                    {expandedSentiment === 'negative' && sentiment.top_negative_sentences && (
                      <div className="mt-2 space-y-2 pl-2 border-l-2 border-red-500/30">
                        {sentiment.top_negative_sentences.map((s, i) => (
                          <div key={i} className="bg-[#0a0a0f] rounded-lg p-3">
                            <p className="text-gray-300 text-sm">{s.text}</p>
                            <p className="text-red-400 text-xs mt-1">Score: {(s.score * 100).toFixed(1)}%</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Summary */}
                <div className="mt-4 pt-4 border-t border-[#2a2a3a]">
                  <p className="text-gray-500 text-sm">
                    Analyzed <span className="text-white font-medium">{sentiment.sentences_analyzed}</span> financial sentences from{" "}
                    <span className="text-blue-400 font-medium">{formatQuarter(actualQuarter || quarter)}</span> earnings call
                  </p>
                  <p className="text-gray-600 text-xs mt-1">Click on each sentiment bar to see sample sentences</p>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">Click "Analyze" to get sentiment from earnings call transcript</p>
              </div>
            )}
          </div>

          {/* Price History */}
          {history.length > 0 && (
            <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Price History (1 Month)</h3>
              <div className="overflow-x-auto">
                <div className="flex gap-1 min-w-max">
                  {history.slice(-30).map((h, i) => {
                    const maxPrice = Math.max(...history.map(p => p.close));
                    const minPrice = Math.min(...history.map(p => p.close));
                    const range = maxPrice - minPrice;
                    const height = ((h.close - minPrice) / range) * 100;

                    return (
                      <div key={i} className="flex flex-col items-center">
                        <div className="w-4 bg-[#2a2a3a] rounded-t relative" style={{ height: "120px" }}>
                          <div
                            className="absolute bottom-0 w-full bg-blue-500 rounded-t"
                            style={{ height: `${height}%` }}
                          />
                        </div>
                        <span className="text-[10px] text-gray-500 mt-1">
                          {new Date(h.date).getDate()}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Empty State */}
      {!quote && !loading && (
        <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-12 text-center">
          <div className="w-16 h-16 rounded-full bg-[#2a2a3a] flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">📈</span>
          </div>
          <p className="text-gray-300 font-medium">Search for a stock symbol</p>
          <p className="text-gray-500 text-sm mt-1">Enter a ticker like AAPL, GOOGL, or MSFT</p>
        </div>
      )}
    </div>
  );
}
