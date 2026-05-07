import { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { productsAPI, reportsAPI } from "../services/api.js";

export const Dashboard = () => {
  const token = useSelector((state) => state.auth.token);
  const [products, setProducts] = useState([]);
  const [lowStock, setLowStock] = useState([]);
  const [movementsSummary, setMovementsSummary] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      if (!token) return;
      try {
        const [prods, low, mov] = await Promise.all([productsAPI.products(), reportsAPI.lowStock(), reportsAPI.movementsSummary()]);
        setProducts(prods || []);
        setLowStock(low || []);
        setMovementsSummary(mov || {});
      } catch (error) {
        console.error("Dashboard load error:", error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [token]);

  if (loading) {
    return <div className="p-12">Loading dashboard...</div>;
  }

  const movements = movementsSummary.movements || [];
  const lowStockItem = lowStock[0];

  return (
    <div className="p-12 max-w-7xl mx-auto">
      <div className="mb-12">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-4">Dashboard</h1>
        <p className="text-xl text-gray-600">Welcome to your inventory control center</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
        <div className="bg-white/80 backdrop-blur-xl p-8 rounded-2xl shadow-xl border border-white/50 hover:shadow-2xl transition-all duration-300">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-xl">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <div className="ml-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">Total Products</h3>
              <p className="text-4xl font-bold text-blue-600">{products.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-xl p-8 rounded-2xl shadow-xl border border-white/50 hover:shadow-2xl">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-xl">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div className="ml-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">Stock Value</h3>
              <p className="text-4xl font-bold text-green-600">$ {movementsSummary.total_value || "0"}</p>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-xl p-8 rounded-2xl shadow-xl border border-white/50 hover:shadow-2xl">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-xl">
              <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                />
              </svg>
            </div>
            <div className="ml-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">Low Stock</h3>
              <p className="text-4xl font-bold text-yellow-600">{lowStock.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white/80 backdrop-blur-xl p-8 rounded-2xl shadow-xl border border-white/50 hover:shadow-2xl">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-xl">
              <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            </div>
            <div className="ml-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-1">Today Orders</h3>
              <p className="text-4xl font-bold text-purple-600">{movementsSummary.total_movements || 0}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Stock Movements</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Qty</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Warehouse</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {movements.slice(0, 5).map((m) => (
                  <tr key={m.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{m.product_name || "N/A"}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">{m.type}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{m.quantity}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{m.warehouse_name || "N/A"}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">{new Date(m.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-yellow-50 rounded-2xl shadow-xl p-8 border border-yellow-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Low Stock Alert</h2>
          <div className="space-y-4">
            {lowStockItem ? (
              <div className="bg-yellow-100 p-4 rounded-xl">
                <div className="font-semibold text-yellow-800">{lowStockItem.product}</div>
                <div className="text-sm text-yellow-700">
                  Qty: {lowStockItem.current_stock} / {lowStockItem.min_level}
                </div>
              </div>
            ) : (
              <div className="bg-green-100 p-4 rounded-xl text-green-800">All stock levels good!</div>
            )}
            <button className="w-full bg-yellow-500 text-white py-3 px-4 rounded-xl font-semibold hover:bg-yellow-600 transition duration-200">Create PO</button>
          </div>
        </div>
      </div>
    </div>
  );
};
