"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";

interface Holding {
  id: number;
  symbol: string;
  quantity: number;
  avg_cost: number;
  current_price: number;
  market_value: number;
  gain_loss: number;
  gain_loss_pct: number;
}

interface Portfolio {
  id: number;
  name: string;
  holdings: Holding[];
  total_value: number;
  total_cost: number;
  total_gain_loss: number;
  total_gain_loss_pct: number;
}

export default function PortfolioPage() {
  const [portfolios, setPortfolios] = useState<{ id: number; name: string }[]>([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newHolding, setNewHolding] = useState({ symbol: "", quantity: 0, avg_cost: 0 });

  const fetchPortfolios = async () => {
    try {
      const data = await api.get("/portfolio/");
      setPortfolios(data);
      if (data.length > 0) {
        const details = await api.get(`/portfolio/${data[0].id}`);
        setSelectedPortfolio(details);
      }
    } catch (error) {
      console.error("Failed to fetch portfolios:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolios();
  }, []);

  const createPortfolio = async () => {
    try {
      await api.post("/portfolio/", { name: "My Portfolio" });
      await fetchPortfolios();
    } catch (error) {
      alert(`Failed to create portfolio: ${error}`);
    }
  };

  const addHolding = async () => {
    if (!selectedPortfolio || !newHolding.symbol) return;

    try {
      await api.post(`/portfolio/${selectedPortfolio.id}/holdings`, {
        holdings: [newHolding],
      });
      const details = await api.get(`/portfolio/${selectedPortfolio.id}`);
      setSelectedPortfolio(details);
      setShowAddForm(false);
      setNewHolding({ symbol: "", quantity: 0, avg_cost: 0 });
    } catch (error) {
      alert(`Failed to add holding: ${error}`);
    }
  };

  if (loading) {
    return (
      <div>
        <h1 className="text-2xl font-bold text-white">Portfolio</h1>
        <p className="text-gray-400 mt-1">Loading...</p>
      </div>
    );
  }

  if (portfolios.length === 0) {
    return (
      <div>
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">Portfolio</h1>
          <p className="text-gray-400 mt-1">Manage your investment portfolio</p>
        </div>

        <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-12 text-center">
          <div className="w-16 h-16 rounded-full bg-[#2a2a3a] flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">💼</span>
          </div>
          <p className="text-gray-300 font-medium">No portfolios yet</p>
          <p className="text-gray-500 text-sm mt-1 mb-4">Create a portfolio to start tracking your investments</p>
          <button
            onClick={createPortfolio}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create Portfolio
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Portfolio</h1>
          <p className="text-gray-400 mt-1">Track your holdings and performance</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          {showAddForm ? "Cancel" : "Add Holding"}
        </button>
      </div>

      {selectedPortfolio && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-[#1a1a24] border border-blue-500/30 rounded-xl p-5">
              <p className="text-gray-400 text-sm">Total Value</p>
              <p className="text-2xl font-bold text-white">${selectedPortfolio.total_value?.toLocaleString()}</p>
            </div>
            <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-5">
              <p className="text-gray-400 text-sm">Total Cost</p>
              <p className="text-2xl font-bold text-white">${selectedPortfolio.total_cost?.toLocaleString()}</p>
            </div>
            <div className={`bg-[#1a1a24] border rounded-xl p-5 ${
              selectedPortfolio.total_gain_loss >= 0 ? "border-green-500/30" : "border-red-500/30"
            }`}>
              <p className="text-gray-400 text-sm">Total Gain/Loss</p>
              <p className={`text-2xl font-bold ${
                selectedPortfolio.total_gain_loss >= 0 ? "text-green-400" : "text-red-400"
              }`}>
                {selectedPortfolio.total_gain_loss >= 0 ? "+" : ""}${selectedPortfolio.total_gain_loss?.toLocaleString()}
              </p>
            </div>
            <div className={`bg-[#1a1a24] border rounded-xl p-5 ${
              selectedPortfolio.total_gain_loss_pct >= 0 ? "border-green-500/30" : "border-red-500/30"
            }`}>
              <p className="text-gray-400 text-sm">Return %</p>
              <p className={`text-2xl font-bold ${
                selectedPortfolio.total_gain_loss_pct >= 0 ? "text-green-400" : "text-red-400"
              }`}>
                {selectedPortfolio.total_gain_loss_pct >= 0 ? "+" : ""}{selectedPortfolio.total_gain_loss_pct?.toFixed(2)}%
              </p>
            </div>
          </div>

          {/* Add Holding Form */}
          {showAddForm && (
            <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl p-5 mb-6">
              <h3 className="text-white font-semibold mb-4">Add Holding</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <input
                  type="text"
                  placeholder="Symbol (e.g., AAPL)"
                  value={newHolding.symbol}
                  onChange={(e) => setNewHolding({ ...newHolding, symbol: e.target.value.toUpperCase() })}
                  className="px-4 py-2 bg-[#0a0a0f] border border-[#2a2a3a] text-white placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="number"
                  placeholder="Quantity"
                  value={newHolding.quantity || ""}
                  onChange={(e) => setNewHolding({ ...newHolding, quantity: parseFloat(e.target.value) || 0 })}
                  className="px-4 py-2 bg-[#0a0a0f] border border-[#2a2a3a] text-white placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="number"
                  placeholder="Avg Cost"
                  value={newHolding.avg_cost || ""}
                  onChange={(e) => setNewHolding({ ...newHolding, avg_cost: parseFloat(e.target.value) || 0 })}
                  className="px-4 py-2 bg-[#0a0a0f] border border-[#2a2a3a] text-white placeholder-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={addHolding}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add
                </button>
              </div>
            </div>
          )}

          {/* Holdings Table */}
          <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-xl overflow-hidden">
            <div className="p-5 border-b border-[#2a2a3a]">
              <h3 className="text-white font-semibold">Holdings</h3>
            </div>
            {selectedPortfolio.holdings.length === 0 ? (
              <div className="p-8 text-center">
                <p className="text-gray-400">No holdings yet. Add your first position above.</p>
              </div>
            ) : (
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#2a2a3a]">
                    <th className="text-left py-4 px-6 text-gray-400 font-medium text-sm">Symbol</th>
                    <th className="text-left py-4 px-6 text-gray-400 font-medium text-sm">Quantity</th>
                    <th className="text-left py-4 px-6 text-gray-400 font-medium text-sm">Avg Cost</th>
                    <th className="text-left py-4 px-6 text-gray-400 font-medium text-sm">Current Price</th>
                    <th className="text-left py-4 px-6 text-gray-400 font-medium text-sm">Market Value</th>
                    <th className="text-left py-4 px-6 text-gray-400 font-medium text-sm">Gain/Loss</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedPortfolio.holdings.map((holding) => (
                    <tr key={holding.id} className="border-b border-[#2a2a3a] hover:bg-[#22222e]">
                      <td className="py-4 px-6 text-white font-medium">{holding.symbol}</td>
                      <td className="py-4 px-6 text-gray-300">{holding.quantity}</td>
                      <td className="py-4 px-6 text-gray-300">${holding.avg_cost?.toFixed(2)}</td>
                      <td className="py-4 px-6 text-gray-300">${holding.current_price?.toFixed(2)}</td>
                      <td className="py-4 px-6 text-white">${holding.market_value?.toLocaleString()}</td>
                      <td className="py-4 px-6">
                        <span className={`px-2 py-1 rounded-full text-sm ${
                          holding.gain_loss >= 0
                            ? "bg-green-500/20 text-green-400"
                            : "bg-red-500/20 text-red-400"
                        }`}>
                          {holding.gain_loss >= 0 ? "+" : ""}${holding.gain_loss?.toFixed(2)} ({holding.gain_loss_pct?.toFixed(2)}%)
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}
