import React, { useState } from "react";
import { BarChart3, TrendingUp, Package, AlertCircle, Download, Calendar } from "lucide-react";
import api from "../../api/axios";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import toast from "react-hot-toast";
import * as XLSX from "xlsx";

const Reports = () => {
  const [reportType, setReportType] = useState("low-stock");
  const [reportData, setReportData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState({
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 16),
    end_date: new Date().toISOString().slice(0, 16),
  });

  const fetchReport = async () => {
    setLoading(true);
    try {
      let response;
      switch (reportType) {
        case "low-stock":
          response = await api.get("/reports/low-stock");
          break;
        case "stock-levels":
          response = await api.get("/reports/stock-levels");
          break;
        case "movements":
          response = await api.get("/reports/inventory-movements", {
            params: { start_date: dateRange.start_date, end_date: dateRange.end_date, limit: 500 },
          });
          break;
        default:
          response = await api.get("/reports/stock-levels");
      }
      setReportData(response.data);
    } catch (error) {
      toast.error("Failed to fetch report");
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchReport();
  }, [reportType]);

  const exportToExcel = () => {
    const ws = XLSX.utils.json_to_sheet(reportData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, reportType);
    XLSX.writeFile(wb, `${reportType}_report_${new Date().toISOString().split("T")[0]}.xlsx`);
    toast.success("Report exported successfully");
  };

  const chartData = [
    { month: "Jan", sales: 4200, purchases: 3800 },
    { month: "Feb", sales: 4500, purchases: 4200 },
    { month: "Mar", sales: 4800, purchases: 4500 },
    { month: "Apr", sales: 5100, purchases: 4900 },
    { month: "May", sales: 5300, purchases: 5100 },
    { month: "Jun", sales: 5600, purchases: 5300 },
  ];

  const pieData = [
    { name: "Electronics", value: 45 },
    { name: "Clothing", value: 25 },
    { name: "Home & Garden", value: 20 },
    { name: "Others", value: 10 },
  ];

  const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Reports & Analytics</h1>
        <button onClick={exportToExcel} className="flex items-center space-x-2 bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors">
          <Download size={20} />
          <span>Export Report</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
            <h3 className="font-semibold mb-3">Report Types</h3>
            <div className="space-y-2">
              {[
                { id: "low-stock", label: "Low Stock Report", icon: AlertCircle },
                { id: "stock-levels", label: "Stock Levels", icon: Package },
                { id: "movements", label: "Inventory Movements", icon: TrendingUp },
                { id: "sales", label: "Sales Report", icon: BarChart3 },
              ].map((report) => (
                <button
                  key={report.id}
                  onClick={() => setReportType(report.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                    reportType === report.id ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600" : "hover:bg-gray-100 dark:hover:bg-gray-700"
                  }`}>
                  <report.icon size={18} />
                  <span className="text-sm">{report.label}</span>
                </button>
              ))}
            </div>
          </div>

          {reportType === "movements" && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 mt-4">
              <h3 className="font-semibold mb-3 flex items-center">
                <Calendar size={16} className="mr-2" />
                Date Range
              </h3>
              <div className="space-y-3">
                <input
                  type="datetime-local"
                  value={dateRange.start_date}
                  onChange={(e) => setDateRange({ ...dateRange, start_date: e.target.value })}
                  className="input-field text-sm"
                />
                <input
                  type="datetime-local"
                  value={dateRange.end_date}
                  onChange={(e) => setDateRange({ ...dateRange, end_date: e.target.value })}
                  className="input-field text-sm"
                />
                <button onClick={fetchReport} className="btn-primary w-full">
                  Apply Filter
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 capitalize">{reportType.replace("-", " ")} Report</h2>

            {/* Charts */}
            <div className="mb-6">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="sales" fill="#3b82f6" name="Sales" />
                  <Bar dataKey="purchases" fill="#10b981" name="Purchases" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Category Distribution */}
            <div className="mb-6">
              <h3 className="font-semibold mb-3">Stock Distribution by Category</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" labelLine={false} label={(entry) => `${entry.name}: ${entry.value}%`} outerRadius={80} fill="#8884d8" dataKey="value">
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Data Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    {reportData[0] &&
                      Object.keys(reportData[0])
                        .slice(0, 6)
                        .map((key) => (
                          <th key={key} className="px-4 py-2 text-left">
                            {key.replace(/_/g, " ").toUpperCase()}
                          </th>
                        ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {reportData.slice(0, 10).map((row, idx) => (
                    <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      {Object.values(row)
                        .slice(0, 6)
                        .map((value, i) => (
                          <td key={i} className="px-4 py-2">
                            {typeof value === "boolean" ? (value ? "Yes" : "No") : typeof value === "object" ? JSON.stringify(value) : value}
                          </td>
                        ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              {loading && <div className="text-center py-8">Loading...</div>}
              {!loading && reportData.length === 0 && <div className="text-center py-8 text-gray-500">No data available</div>}
              {reportData.length > 10 && <div className="text-center py-4 text-sm text-gray-500">Showing 10 of {reportData.length} records</div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reports;
