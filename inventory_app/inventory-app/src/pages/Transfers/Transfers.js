import React, { useState, useEffect } from "react";
import { Plus, ArrowRight, CheckCircle, XCircle } from "lucide-react";
import api from "../../api/axios";
import Modal from "../../components/Common/Modal";
import toast from "react-hot-toast";

const Transfers = () => {
  const [transfers, setTransfers] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    from_warehouse_id: "",
    to_warehouse_id: "",
    product_id: "",
    quantity: 1,
  });

  useEffect(() => {
    fetchTransfers();
    fetchWarehouses();
    fetchProducts();
  }, []);

  const fetchTransfers = async () => {
    try {
      const response = await api.get("/transfer-orders");
      setTransfers(response.data);
    } catch (error) {
      toast.error("Failed to fetch transfers");
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

  const fetchProducts = async () => {
    try {
      const response = await api.get("/products");
      setProducts(response.data);
    } catch (error) {
      console.error("Failed to fetch products", error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.from_warehouse_id === formData.to_warehouse_id) {
      toast.error("Source and destination warehouses cannot be the same");
      return;
    }
    try {
      await api.post("/transfer-orders", formData);
      toast.success("Transfer order created successfully");
      fetchTransfers();
      setShowModal(false);
      setFormData({ from_warehouse_id: "", to_warehouse_id: "", product_id: "", quantity: 1 });
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create transfer");
    }
  };

  const completeTransfer = async (transferId) => {
    if (window.confirm("Complete this transfer?")) {
      try {
        await api.post(`/transfer-orders/${transferId}/complete`);
        toast.success("Transfer completed successfully");
        fetchTransfers();
      } catch (error) {
        toast.error("Failed to complete transfer");
      }
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: "bg-yellow-100 text-yellow-800",
      in_transit: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      cancelled: "bg-red-100 text-red-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const getProductName = (productId) => {
    const product = products.find((p) => p.id === productId);
    return product?.name || `Product #${productId}`;
  };

  const getWarehouseName = (warehouseId) => {
    const warehouse = warehouses.find((w) => w.id === warehouseId);
    return warehouse?.name || `Warehouse #${warehouseId}`;
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
        <h1 className="text-2xl font-bold">Stock Transfers</h1>
        <button onClick={() => setShowModal(true)} className="flex items-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
          <Plus size={20} />
          <span>Create Transfer</span>
        </button>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Transfer #</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Product</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">From → To</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Quantity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {transfers.map((transfer) => (
                <tr key={transfer.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{transfer.transfer_number}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{getProductName(transfer.product_id)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center space-x-2">
                      <span>{getWarehouseName(transfer.from_warehouse_id)}</span>
                      <ArrowRight size={14} />
                      <span>{getWarehouseName(transfer.to_warehouse_id)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{transfer.quantity}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(transfer.status)}`}>{transfer.status}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{new Date(transfer.created_at).toLocaleDateString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {transfer.status === "pending" && (
                      <button onClick={() => completeTransfer(transfer.id)} className="text-green-500 hover:text-green-700">
                        <CheckCircle size={18} />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {transfers.length === 0 && <div className="text-center py-8 text-gray-500">No transfer orders found</div>}
      </div>

      {/* Create Transfer Modal */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Create Stock Transfer">
        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">From Warehouse *</label>
              <select value={formData.from_warehouse_id} onChange={(e) => setFormData({ ...formData, from_warehouse_id: e.target.value })} className="input-field" required>
                <option value="">Select Source Warehouse</option>
                {warehouses.map((warehouse) => (
                  <option key={warehouse.id} value={warehouse.id}>
                    {warehouse.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">To Warehouse *</label>
              <select value={formData.to_warehouse_id} onChange={(e) => setFormData({ ...formData, to_warehouse_id: e.target.value })} className="input-field" required>
                <option value="">Select Destination Warehouse</option>
                {warehouses.map((warehouse) => (
                  <option key={warehouse.id} value={warehouse.id}>
                    {warehouse.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Product *</label>
              <select value={formData.product_id} onChange={(e) => setFormData({ ...formData, product_id: e.target.value })} className="input-field" required>
                <option value="">Select Product</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name} ({product.sku})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Quantity *</label>
              <input
                type="number"
                value={formData.quantity}
                onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) })}
                className="input-field"
                min="1"
                step="1"
                required
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Transfer
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Transfers;
