import React, { useState, useEffect } from "react";
import { AlertCircle, CheckCircle, Settings } from "lucide-react";
import api from "../../api/axios";
import Modal from "../../components/Common/Modal";
import toast from "react-hot-toast";

const Stock = () => {
  const [stockItems, setStockItems] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [selectedWarehouse, setSelectedWarehouse] = useState("");
  const [showAdjustModal, setShowAdjustModal] = useState(false);
  const [selectedStock, setSelectedStock] = useState(null);
  const [adjustmentData, setAdjustmentData] = useState({ type: "increase", quantity: 0, reason: "" });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStock();
    fetchWarehouses();
  }, [selectedWarehouse]);

  const fetchStock = async () => {
    try {
      const params = selectedWarehouse ? { warehouse_id: selectedWarehouse } : {};
      const response = await api.get("/stock", { params });
      setStockItems(response.data);
    } catch (error) {
      toast.error("Failed to fetch stock data");
    } finally {
      setLoading(false);
    }
  };

  const fetchWarehouses = async () => {
    try {
      const response = await api.get("/warehouses");
      setWarehouses(response.data);
    } catch (error) {
      console.error("Failed to fetch warehouses", error);
    }
  };

  const handleAdjustStock = async () => {
    try {
      await api.post("/stock-adjustments", {
        product_id: selectedStock.product_id,
        warehouse_id: selectedStock.warehouse_id,
        adjustment_type: adjustmentData.type,
        quantity: adjustmentData.quantity,
        reason: adjustmentData.reason,
      });
      toast.success("Stock adjusted successfully");
      fetchStock();
      setShowAdjustModal(false);
      setAdjustmentData({ type: "increase", quantity: 0, reason: "" });
    } catch (error) {
      toast.error("Failed to adjust stock");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Stock Management</h1>
        <div className="flex space-x-3">
          <select
            value={selectedWarehouse}
            onChange={(e) => setSelectedWarehouse(e.target.value)}
            className="px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">All Warehouses</option>
            {warehouses.map((warehouse) => (
              <option key={warehouse.id} value={warehouse.id}>
                {warehouse.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Product</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Warehouse</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Quantity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Available</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Reorder Point</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {stockItems.map((item, index) => (
                <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="font-medium">{item.product_name}</div>
                    <div className="text-xs text-gray-500">{item.sku}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{item.warehouse_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{Math.round(item.quantity)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{Math.round(item.available_quantity)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{Math.round(item.reorder_point)}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {item.quantity <= item.reorder_point ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                        <AlertCircle size={12} className="mr-1" />
                        Low Stock
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                        <CheckCircle size={12} className="mr-1" />
                        Normal
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => {
                        setSelectedStock(item);
                        setShowAdjustModal(true);
                      }}
                      className="text-blue-500 hover:text-blue-700 transition-colors">
                      <Settings size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {stockItems.length === 0 && <div className="text-center py-8 text-gray-500">No stock records found</div>}
      </div>

      <Modal isOpen={showAdjustModal} onClose={() => setShowAdjustModal(false)} title="Adjust Stock">
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-500">Product</p>
            <p className="font-medium">{selectedStock?.product_name}</p>
          </div>

          <div>
            <p className="text-sm text-gray-500">Current Stock</p>
            <p className="font-medium">{selectedStock?.quantity} units</p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Adjustment Type</label>
            <select value={adjustmentData.type} onChange={(e) => setAdjustmentData({ ...adjustmentData, type: e.target.value })} className="input-field">
              <option value="increase">Increase (+)</option>
              <option value="decrease">Decrease (-)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Quantity</label>
            <input
              type="number"
              value={adjustmentData.quantity}
              onChange={(e) => setAdjustmentData({ ...adjustmentData, quantity: parseFloat(e.target.value) })}
              className="input-field"
              min="0"
              step="1"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Reason</label>
            <textarea
              value={adjustmentData.reason}
              onChange={(e) => setAdjustmentData({ ...adjustmentData, reason: e.target.value })}
              className="input-field"
              rows="3"
              placeholder="Enter reason for adjustment..."
            />
          </div>
        </div>

        <div className="flex justify-end space-x-3 mt-6">
          <button onClick={() => setShowAdjustModal(false)} className="btn-secondary">
            Cancel
          </button>
          <button onClick={handleAdjustStock} className="btn-primary">
            Submit Adjustment
          </button>
        </div>
      </Modal>
    </div>
  );
};

export default Stock;
