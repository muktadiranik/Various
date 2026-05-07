import React, { useState, useEffect } from "react";
import { Package, AlertCircle, ShoppingCart, TrendingUp, Warehouse, Users, DollarSign, Boxes } from "lucide-react";
import api from "../api/axios";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_products: 0,
    low_stock_alerts: 0,
    pending_purchase_orders: 0,
    pending_sales_orders: 0,
    total_warehouses: 0,
    total_suppliers: 0,
    total_customers: 0,
  });
  const [recentMovements, setRecentMovements] = useState([]);
  const [lowStockItems, setLowStockItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, movementsRes, lowStockRes] = await Promise.all([
        api.get("/dashboard/stats"),
        api.get("/activity-logs", { params: { limit: 10 } }),
        api.get("/reports/low-stock"),
      ]);
      setStats(statsRes.data);
      setRecentMovements(movementsRes.data);
      setLowStockItems(lowStockRes.data);
    } catch (error) {
      console.error("Failed to fetch dashboard data", error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    { title: "Total Products", value: stats.total_products, icon: Package, color: "bg-blue-500" },
    { title: "Low Stock Alerts", value: stats.low_stock_alerts, icon: AlertCircle, color: "bg-red-500" },
    { title: "Pending POs", value: stats.pending_purchase_orders, icon: ShoppingCart, color: "bg-orange-500" },
    { title: "Pending SOs", value: stats.pending_sales_orders, icon: TrendingUp, color: "bg-green-500" },
    { title: "Warehouses", value: stats.total_warehouses, icon: Warehouse, color: "bg-purple-500" },
    { title: "Suppliers", value: stats.total_suppliers, icon: Users, color: "bg-indigo-500" },
  ];

  const chartData = [
    { name: "Jan", sales: 4000, purchases: 2400 },
    { name: "Feb", sales: 3000, purchases: 1398 },
    { name: "Mar", sales: 2000, purchases: 9800 },
    { name: "Apr", sales: 2780, purchases: 3908 },
    { name: "May", sales: 1890, purchases: 4800 },
    { name: "Jun", sales: 2390, purchases: 3800 },
  ];

  const pieData = [
    { name: "Electronics", value: 400 },
    { name: "Clothing", value: 300 },
    { name: "Home & Garden", value: 200 },
    { name: "Others", value: 100 },
  ];

  const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400">Welcome back! Here's your inventory overview.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
        {statCards.map((card, index) => (
          <div key={index} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide">{card.title}</p>
                <p className="text-2xl font-bold mt-1">{card.value}</p>
              </div>
              <div className={`${card.color} p-3 rounded-full text-white`}>
                <card.icon size={20} />
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold mb-4">Sales vs Purchases</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="sales" fill="#3b82f6" />
              <Bar dataKey="purchases" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold mb-4">Stock by Category</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" labelLine={false} label={(entry) => entry.name} outerRadius={100} fill="#8884d8" dataKey="value">
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md">
          <div className="p-4 border-b dark:border-gray-700">
            <h2 className="text-lg font-semibold">Low Stock Alerts</h2>
          </div>
          <div className="divide-y dark:divide-gray-700">
            {lowStockItems.slice(0, 5).map((item, index) => (
              <div key={index} className="p-4 flex justify-between items-center">
                <div>
                  <p className="font-medium">{item.product_name}</p>
                  <p className="text-sm text-gray-500">SKU: {item.sku}</p>
                </div>
                <div className="text-right">
                  <p className="text-red-600 font-semibold">{item.current_stock} units</p>
                  <p className="text-xs text-gray-500">Reorder at: {item.reorder_point}</p>
                </div>
              </div>
            ))}
            {lowStockItems.length === 0 && <div className="p-4 text-center text-gray-500">No low stock alerts</div>}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md">
          <div className="p-4 border-b dark:border-gray-700">
            <h2 className="text-lg font-semibold">Recent Activity</h2>
          </div>
          <div className="divide-y dark:divide-gray-700 max-h-96 overflow-y-auto">
            {recentMovements.map((movement) => (
              <div key={movement.id} className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium capitalize">{movement.action?.replace(/_/g, " ")}</p>
                    <p className="text-sm text-gray-500">{movement.entity_type}</p>
                  </div>
                  <p className="text-xs text-gray-500">{new Date(movement.timestamp).toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
